#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

from . import protocol

REPORT_KEY0_ID = 'KEY0'
REPORT_KEY1_ID = 'KEY1'


class Keys(object):
    def __init__(self):
        pass

    def register_key0_callback(self, callback=None):
        return self._register_report_callback(REPORT_KEY0_ID, callback)

    def register_key1_callback(self, callback=None):
        return self._register_report_callback(REPORT_KEY1_ID, callback)

    def set_report_keys(self, on=True, is_on=None):
        on = is_on if is_on is not None else on
        assert isinstance(on, bool) or (isinstance(on, int) and on >= 0)
        cmd = protocol.SET_REPORT_KEYS.format(int(not is_on))
        return self.send_cmd_sync(cmd)

