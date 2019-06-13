#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFactory, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import os
import sys
import time
import functools
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI

"""
api test: report callback
"""


def power_callback(ret):
    print('report power: {}, time: {}'.format(ret, time.time()))


def pos_callback(ret):
    print('report pos: {}, time: {}'.format(ret, time.time()))


def key_callback(ret, key=None):
    print('report {}: {}, time: {}'.format(key, ret, time.time()))


def limit_switch_callback(ret):
    print('report limit switch: {}, time: {}'.format(ret, time.time()))


swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, do_not_open=True)
swift.register_power_callback(callback=power_callback)
# swift.register_report_position_callback(callback=pos_callback)
swift.register_key0_callback(callback=functools.partial(key_callback, key='key0'))
swift.register_key1_callback(callback=functools.partial(key_callback, key='key1'))
swift.register_limit_switch_callback(callback=limit_switch_callback)
swift.connect()
swift.waiting_ready()

swift.set_report_position(interval=0.1)
swift.set_report_keys(on=True)
swift.set_servo_detach()


time.sleep(60)

swift.set_report_position(interval=0)
swift.set_report_keys(on=False)
swift.set_servo_attach()

swift.disconnect()
