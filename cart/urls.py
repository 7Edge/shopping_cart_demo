#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: urls
# Date: 3/25/2019

from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt
from cart.views import shoppingcart
from cart.views import account
from cart.views import payment_center

urlpatterns = [
    re_path('^shopping_cart/$', csrf_exempt(shoppingcart.ShoppingCartAPIView.as_view())),
    re_path('^access_token/$', csrf_exempt(account.AccessTokenAPIView.as_view()), name='access_token'),
    re_path('^payment/$', payment_center.PaymentCenterViewSet.as_view(actions={'post': 'create',
                                                                               'get': 'list'})),
]
if __name__ == '__main__':
    pass
