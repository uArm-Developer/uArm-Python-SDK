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
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from uarm.wrapper import SwiftAPI


swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})


def power_callback(ret):
    print('power:', ret)
    if ret:
        swift.set_report_position(0.5)
        swift.set_report_keys()
    else:
        swift.set_report_position(0)
        swift.set_report_keys(False)


def pos_callback(pos):
    print('pos:', pos)


def key_callback(ret, key=None):
    print('{}: {}'.format(key, ret))


def limit_switch_callback(ret):
    print('limit switch:', ret)

swift.register_power_callback(power_callback)
swift.register_report_position_callback(pos_callback)
swift.register_key0_callback(functools.partial(key_callback, key='key0'))
swift.register_key1_callback(functools.partial(key_callback, key='key1'))
swift.register_limit_switch(functools.partial(limit_switch_callback))

import threading
while True:
    time.sleep(1)
    print('>>>', len(threading.enumerate()))
