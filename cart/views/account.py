#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: account
# Date: 3/26/2019
"""
获取令牌
"""
import uuid

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework.views import APIView

from cart.utils.response import AccessTokenResponse
from cart import models
from cart.serializers import account_serializer
from cart.utils.china_time import china_current


class AccessTokenAPIView(APIView):

    def post(self, request, *args, **kwargs):
        # print("请求的编码类型", request._request.content_type)

        result = AccessTokenResponse()
        result.code = 1000

        serializer_obj = account_serializer.UserPwdSerializer(data=request.data, many=False)
        if serializer_obj.is_valid():
            try:
                user = models.UserInfo.objects.get(**serializer_obj.validated_data)
                token_obj, is_create = models.UserToken.objects.update_or_create(user=user,
                                                                                 defaults={"token": str(uuid.uuid4()),
                                                                                           "expired": china_current.add(
                                                                                               days=2)})
            except ObjectDoesNotExist:
                result.code = 1001
                result.error = '用户名或密码错误！'
            else:
                result.access_token = token_obj.token
                result.expiry = token_obj.expired.strftime('%Y-%m-%d %H:%M:%S %Z')
        else:
            result.code = 1002
            result.error = "用户名或密码格式错误！"
        return Response(result.dict)


if __name__ == '__main__':
    pass
