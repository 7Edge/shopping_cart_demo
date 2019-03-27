#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: response
# Date: 3/26/2019


class BaseResponse(object):

    def __init__(self):
        self.code = None
        self.error = None

    @property
    def dict(self):
        return self.__dict__


class AccessTokenResponse(BaseResponse):

    def __init__(self):
        super(AccessTokenResponse, self).__init__()
        self.access_token = ""
        self.expiry = ""


if __name__ == '__main__':
    pass
