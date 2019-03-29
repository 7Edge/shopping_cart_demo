#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: shopping_cart_serializer
# Date: 3/28/2019

from rest_framework import serializers

from cart import models


# 价格策略序列化
class PricePolicyModelSerializer(serializers.ModelSerializer):
    period_str = serializers.CharField(source='get_period_display')

    class Meta:
        model = models.PricePolicy
        fields = ['id', 'period', 'period_str', 'price']


# 学位课程购物车序列化
class ShoppingCartCourseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    course_img = serializers.CharField(max_length=255)

    degree_price_policy_qs = serializers.SerializerMethodField()

    def get_degree_price_policy_qs(self, obj):
        return PricePolicyModelSerializer(obj.degree_price_policy_qs.all(), many=True).data


if __name__ == '__main__':
    pass
