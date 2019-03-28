#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: AccessTokenAuth
# Date: 3/28/2019
"""

"""
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from cart import models

from cart.utils import china_time


class AccessTokenAuth(BaseAuthentication):

    def authenticate(self, request):
        # try:
        #     access_token = request.query_param.get('access_token')
        #     token_obj = models.UserToken.objects.get(access_token=access_token)
        #     if china_time.china_current.now <= token_obj.expired:
        #         return token_obj.user, token_obj.token
        #     raise exceptions.AuthenticationFailed('access_token已过期！')
        # except ObjectDoesNotExist:
        #     raise exceptions.AuthenticationFailed('access_token无效！')

        access_token = request.query_params.get('access_token')
        token_obj = models.UserToken.objects.filter(expired__gte=china_time.china_current.now,
                                                    toke=access_token).first()
        if token_obj:
            return token_obj.user, token_obj.token
        else:
            raise exceptions.AuthenticationFailed('access_token无效！')


if __name__ == '__main__':
    pass
