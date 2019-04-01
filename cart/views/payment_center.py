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
from cart.serializers import coupon_serializer


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

        redis_conn = get_redis_connection()
        # 格式化得到商品在redis中的key列表
        course_keys = [settings.SHOPPING_CART_KEY.format(user_id=user_obj.pk,
                                                         course_id=item) for item in course_list]
        # 1. 检查id是否在购物车中
        if redis_conn.exists(*course_keys) != len(course_keys):
            return Response({'code': 1001,
                             'error': '商品购物车中不存在!'})

        # 2. 获取到"用户"的"有效优惠券"列表（暂时不关联商品，因为商品和优惠卷的关联，前端做！）
        course_id_key_map = dict(zip(course_list, course_keys))
        to_day = china_current.now.date()  # 当前date
        in_payment_product = []
        for k_id, v_key in course_id_key_map.items():
            """
            遍历处理商品，最终加入到结算中心
            """
            coupon_record_qs = models.CouponRecord.objects.filter(account=user_obj,
                                                                  status=0, coupon__valid_begin_date__lte=to_day,
                                                                  coupon__valid_end_date__gte=to_day)
            # 序列化优惠卷
            coupon_serializer_obj = coupon_serializer.CouponRecordModelSerializer(coupon_record_qs, many=True)

            # 改变优惠卷列表 为 字典形式存储, 即：{优惠券id: "{优惠券其它信息}",...}
            coupon_dict = dict()
            for item in coupon_serializer_obj.data:
                coupon_id = item.pop('id')
                coupon_dict[coupon_id] = json.dumps(item)

            coupon_dict[0] = None  # 提供不适用优惠卷，即0优惠券

            # 获取购物车中存储的商品信息
            product = dict([(k.decode('utf8'), v.decode('utf8')) for k, v in redis_conn.hgetall(v_key).items()])

            # 将购物车中商品的价格策略信息取出提升到商品信息侧面
            price_policy = json.loads(product.pop('degree_price_policy_qs'))
            curr_policy_id = product['policy_id']
            product.update(price_policy[curr_policy_id])

            # 最后将处理好的优惠卷信息放入到商品信息中
            product['coupons'] = json.dumps(coupon_dict)

            # 将要结算的商品放入redis,key信息在settings中设置了
            payment_key = settings.PAYMENT_CENTER_KEY.format(user_id=user_obj.pk, course_id=k_id)
            redis_conn.hmset(payment_key, product)

            in_payment_product.append(product)

        return Response({"code": 1000,
                         "data": in_payment_product})


if __name__ == '__main__':
    pass
