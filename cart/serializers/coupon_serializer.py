#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: coupon_serializer
# Date: 3/29/2019
"""
优惠券 序列化
"""

from rest_framework import serializers

from cart import models


# 优惠券记录序列化

class CouponRecordModelSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='__str__')
    brief = serializers.CharField(source='coupon.brief')
    coupon_type = serializers.IntegerField(source='coupon.coupon_type')
    coupon_type_name = serializers.CharField(source='coupon.get_coupon_type_display')

    class Meta:
        model = models.CouponRecord
        fields = '__all__'


if __name__ == '__main__':
    pass
