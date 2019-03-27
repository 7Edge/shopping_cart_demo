#!/usr/bin/env python
# coding=UTF-8
# author: zhangjiaqi <1399622866@qq.com>
# File: china_time
# Date: 3/27/2019
"""
提供中国时区的时间及常用操作
"""
import datetime
import pytz

CHINA_TIMEZONE = pytz.timezone('Asia/Shanghai')


class ChinaCurrentTime(object):

    @property
    def now(self):
        return datetime.datetime.now(CHINA_TIMEZONE)

    def add(self, *args, **kwargs):
        return self.now + datetime.timedelta(*args, **kwargs)


china_current = ChinaCurrentTime()

if __name__ == '__main__':
    pass
