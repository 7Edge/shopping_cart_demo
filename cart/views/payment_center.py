#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: payment_center
# Date: 3/29/2019
"""
结算中心
"""

import json

from django.conf import settings
from django_redis import get_redis_connection

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from cart.utils.china_time import china_current
from cart.authentication.auth import AccessTokenAuth
from cart import models

redis_conn = get_redis_connection()


class PaymentCenterViewSet(ViewSet):
    authentication_classes = [AccessTokenAuth, ]

    def create(self, request, *args, **kwargs):
        """
        将购物车选中商品，加入到用户结算中心:
        1. 先做post数据的合法性
        2. 处理
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        user_obj = request.user
        course_list = request.data.getlist('course_list')

        # 格式化得到商品在redis中的key列表
        course_keys = [settings.SHOPPING_CART_KEY.format(user_id=user_obj.pk,
                                                         course_id=item) for item in course_list]
        # 1. 检查id是否在购物车中
        if redis_conn.exists(*course_keys) != len(course_keys):
            return Response({'code': 1001,
                             'error': '商品购物车中不存在!'})
        # 2. 构建存储结构
        in_payment_product_space = dict()  # 用于存放所有结算中心的商品信息和全局优惠券
        global_coupons = {
            'coupons': {},
            'default_coupon': 0
        }

        # 3. 遍历处理购物车商品
        course_id_key_map = dict(zip(course_list, course_keys))

        for k_id, v_key in course_id_key_map.items():
            """
            遍历处理商品
            """
            # 获取购物车中存储的商品信息
            product = dict([(k.decode('utf8'), v.decode('utf8')) for k, v in redis_conn.hgetall(v_key).items()])

            # 将购物车中商品的价格策略信息取出提升到商品信息侧面
            price_policy = json.loads(product.pop('degree_price_policy_qs'))
            curr_policy_id = product['policy_id']
            product.update(price_policy[curr_policy_id])

            # 给商品指定一个默认优惠卷0
            product['default_coupon'] = 0

            product['coupons'] = dict()

            in_payment_product_space[str(k_id)] = product

        # 4. 获取到"用户"的"有效优惠券"列表,
        to_day = china_current.now.date()  # 当前date
        coupon_record_qs = models.CouponRecord.objects.filter(account=user_obj,
                                                              status=0, coupon__valid_begin_date__lte=to_day,
                                                              coupon__valid_end_date__gte=to_day).select_related(
            'coupon')  # 这里主动关联coupon

        # 4.1 处理每一个优惠卷，将他们进行商品和通用分类

        for coupon_item in coupon_record_qs:
            # 课程id
            coupon_course_id = coupon_item.coupon.object_id

            if coupon_course_id and str(coupon_course_id) not in course_list:  # 优惠券绑定的课程不在购物车
                continue

            # 构造优惠卷结构
            coupon_info = dict()
            # 优惠券类型
            coupon_type = coupon_item.coupon.coupon_type
            coupon_info['coupon_type'] = coupon_type
            coupon_info['coupon_display'] = coupon_item.coupon.get_coupon_type_display()

            if coupon_type == 0:  # 立减
                coupon_info['money_equivalent_value'] = coupon_item.coupon.money_equivalent_value
            elif coupon_type == 1:
                coupon_info['money_equivalent_value'] = coupon_item.coupon.money_equivalent_value
                coupon_info['minimum_consume'] = coupon_item.coupon.minimum_consume
            else:
                coupon_info['off_percent'] = coupon_item.coupon.off_percent

            # 优惠卷ID
            coupon_id = str(coupon_item.id)
            # 将优惠券分类放入到各自的位置
            if not coupon_course_id:  # 通用优惠券
                global_coupons['coupons'][coupon_id] = coupon_info
            else:
                in_payment_product_space[str(coupon_course_id)]['coupons'][coupon_id] = coupon_info

        # 将要结算的商品放入redis,key信息在settings中设置了
        for k_course_id, v_product in in_payment_product_space.items():
            payment_key = settings.PAYMENT_CENTER_KEY.format(user_id=user_obj.pk, course_id=k_course_id)
            v_product['coupons'] = json.dumps(v_product['coupons'])
            redis_conn.hmset(payment_key, v_product)

        # 将全局优惠券放入redis
        global_coupons_key = settings.USER_GLOBAL_COUPON_KEY.format(user_id=user_obj.pk)
        global_coupons['coupons'] = json.dumps(global_coupons['coupons'])
        redis_conn.hmset(global_coupons_key, global_coupons)

        return Response({"code": 1000,
                         "data": "添加成功"})

    def list(self, request, *args, **kwargs):
        user_obj = request.user

        data = []

        for item in redis_conn.scan_iter(settings.PAYMENT_CENTER_KEY.format(user_id=user_obj.pk,
                                                                            course_id='*'), count=2):
            info = {}
            for k, v in redis_conn.hgetall(item).items():
                k = k.decode(encoding='utf8')
                v = v.decode(encoding='utf8')
                if k == "coupons":
                    info[k] = json.loads(v)
                else:
                    info[k] = v
            data.append(info)

        return Response({"code": 1000,
                         "data": data})

    # def update(self, request, *args, **kwargs):
    #     """
    #     更新优惠卷,绑定商品和通用优惠卷都一起，通用优惠卷的商品course_id = 0 代表 是通用优惠卷的修改
    #     :param request:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     user_obj = request.user
    #
    #     course_id = request.data.get('course_id')
    #     coupon_id = str(request.data.get('coupon_id'))
    #
    #     # 校验商品和优惠卷的合法性
    #     course_key = settings.PAYMENT_CENTER_KEY.format(user_id=user_obj.pk,
    #                                                     course_id=course_id)
    #
    #     coupons = redis_conn.hget(course_key, 'coupons')


if __name__ == '__main__':
    pass
