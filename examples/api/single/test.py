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

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})
# swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, enable_handle_thread=False)
# swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, enable_write_thread=True)
# swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, enable_report_thread=True)
# swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, enable_handle_thread=True, enable_write_thread=True, enable_report_thread=True)

swift.waiting_ready()

# print(swift.get_device_info())

# swift.set_mode(0)
#
# swift.set_servo_detach()
# time.sleep(2)
#
# start_time = time.time()
# swift.reset(speed=100000, wait=False)
# print(time.time() - start_time)

import threading
while True:
    print('thread count:', len(threading.enumerate()))
    time.sleep(1)

