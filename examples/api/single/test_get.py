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
api test: get
"""

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

swift.waiting_ready()

ret = swift.get_power_status()
print('power status: {}'.format(ret))

ret = swift.get_device_info()
print('device info: {}'.format(ret))
ret = swift.get_limit_switch()
print('limit switch: {}'.format(ret))
ret = swift.get_gripper_catch()
print('gripper catch: {}'.format(ret))
ret = swift.get_mode()
print('mode: {}'.format(ret))
print('set mode:', swift.set_mode(1))
ret = swift.get_mode()
print('mode: {}'.format(ret))
ret = swift.get_servo_attach(servo_id=2)
print('servo attach: {}'.format(ret))
ret = swift.get_servo_angle()
print('servo angle: {}'.format(ret))


def print_callback(ret, key=None):
    print('{}: {}'.format(key, ret))

swift.get_polar(wait=False, callback=functools.partial(print_callback, key='polar'))
swift.get_position(wait=False, callback=functools.partial(print_callback, key='position'))

swift.flush_cmd()
swift.disconnect()

