#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: shoppingcart
# Date: 3/25/2019
"""
1. 添加到购物车
2. 查看购物车
3. 修改购物车
3. 删除购物车
"""

import json
import copy

from rest_framework.views import APIView
from rest_framework.response import Response

from cart.authentication.auth import AccessTokenAuth

from django.conf import settings
from django_redis import get_redis_connection
from django.core.exceptions import ObjectDoesNotExist

from cart import models
from cart.serializers.shopping_cart_serializer import ShoppingCartCourseSerializer


class ShoppingCartAPIView(APIView):
    authentication_classes = [AccessTokenAuth, ]

    def get(self, request, *args, **kwargs):
        user_obj = request.user

        redis_conn = get_redis_connection()

        data = list()

        for item in redis_conn.scan_iter(settings.SHOPPING_CART_KEY.format(user_id=user_obj.pk,
                                                                           course_id='*')):
            info = {}
            for k, v in redis_conn.hgetall(item).items():
                k = k.decode(encoding='utf8')
                v = v.decode(encoding='utf8')
                if k == "degree_price_policy_qs":
                    info[k] = json.loads(v)
                else:
                    info[k] = v
            data.append(info)

        return Response({'code': 1000,
                         'data': data})

    def post(self, request, *args, **kwargs):
        user_obj = request.user
        course_id = request.data.get('course_id')
        pricepolicy_id = request.data.get('pricepolicy_id')

        try:
            course_obj = models.DegreeCourse.objects.get(pk=course_id)
        except ObjectDoesNotExist:
            return Response({'code': 1002,
                             'error': '商品ID不存在！'})

        data = ShoppingCartCourseSerializer(course_obj, many=False).data

        policy_dict = dict()
        for item in data['degree_price_policy_qs']:
            n_id = item.pop('id')
            policy_dict[n_id] = item
        data['policy_id'] = pricepolicy_id

        new_data = copy.deepcopy(data)

        data['degree_price_policy_qs'] = json.dumps(policy_dict)
        new_data['degree_price_policy_qs'] = policy_dict
        if course_obj.degree_price_policy_qs.filter(pk=pricepolicy_id).exists():
            redis_conn = get_redis_connection()
            key = settings.SHOPPING_CART_KEY.format(user_id=user_obj.pk,
                                                    course_id=course_id,
                                                    )

            redis_conn.hmset(key, data)
            return Response({'code': 1000,
                             'data': new_data})
        else:
            return Response({'code': 1001,
                             'error': '商品类型不存在'})

    def patch(self, request, *args, **kwargs):
        """
        由于商品只有价格可以修改
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user_obj = request.user
        coures_id = request.data.get('coures_id')
        price_id = request.data.get('price_id')

        # 1. 拼接key
        course_key = settings.SHOPPING_CART_KEY.format(user_id=user_obj.pk,
                                                       course_id=coures_id)
        # 2. 商品存在于购物车
        redis_conn = get_redis_connection()
        if not redis_conn.exists(course_key):
            return Response({'code': 1001,
                             'error': '商品不在购物车中！'})
        # 3. 更新的价格策略是否在策略集中
        price_policy = json.loads(redis_conn.hget(course_key, 'degree_price_policy_qs').decode('utf8'))
        if str(price_id) in price_policy:
            redis_conn.hset(course_key, 'policy_id', price_id)
            return Response('修改成功')
        else:
            return Response('价格策略不存在！')

    def delete(self, request, *args, **kwargs):
        user_obj = request.user
        course_id = request.data.get('course_id')

        redis_conn = get_redis_connection()
        redis_conn.delete(settings.SHOPPING_CART_KEY.format(user_id=user_obj.pk,
                                                            course_id=course_id))
        return Response('删除成功！')


if __name__ == '__main__':
    pass
