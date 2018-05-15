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
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import threading
from uarm.wrapper import SwiftAPI


swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

count = 0
while True:
    # print('111>>>', len(threading.enumerate()))
    swift.connect()
    # while not swift.power_status:
    #     time.sleep(0.01)
    # print(swift.get_device_info())
    if count == 5:
        break
    # print('222>>>', len(threading.enumerate()))
    swift.disconnect()
    # print('333>>>', len(threading.enumerate()))
    count += 1


while not swift.power_status:
    time.sleep(0.01)
print(swift.get_device_info())
swift.set_position(x=200, y=100, speed=5000, wait=True, timeout=20)



