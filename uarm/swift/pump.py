#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

from . import protocol

REPORT_LIMIT_SWITCH_ID = 'LIMIT_SWITCH'


class Pump(object):
    def __init__(self):
        pass

    def register_limit_switch(self, callback=None):
        return self._register_report_callback(REPORT_LIMIT_SWITCH_ID, callback)

    def set_pump(self):
        pass

    def get_limit_switch(self):
        pass
