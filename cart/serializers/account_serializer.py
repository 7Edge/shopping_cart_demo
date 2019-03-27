#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: account_serializer
# Date: 3/26/2019
from rest_framework import serializers


class UserPwdSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=64)
    pwd = serializers.CharField(max_length=64)


if __name__ == '__main__':
    pass
