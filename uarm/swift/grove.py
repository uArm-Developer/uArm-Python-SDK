#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

from . import protocol

REPORT_GROVE_ID = 'GROVE'


class Grove(object):
    def __init__(self):
        pass

    def groce_init(self, pin=None, grove_id=None, value=None):
        pass

    def grove_control(self):
        pass

    def register_grove_callback(self, grove_id=None, callback=None):
        return self._register_report_callback(REPORT_GROVE_ID + '_{}'.format(grove_id), callback)

    def set_report_grove(self, grove_id=None, interval=0.5):
        assert isinstance(interval, (int, float)) and interval >= 0
        cmd = protocol.SET_GROVE_REPORT.format(grove_id, interval)
        return self.send_cmd_sync(cmd)



