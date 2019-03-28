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
from rest_framework.views import APIView

from cart.authentication.auth import AccessTokenAuth


class ShoppingCartAPIView(APIView):
    authentication_classes = [AccessTokenAuth, ]

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass

    def patch(self, request, *args, **kwargs):
        pass

    def delete(self, request, *args, **kwargs):
        pass


if __name__ == '__main__':
    pass
