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
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI

"""
api test: only support firmware version less than 4.0 temporarily
"""

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

swift.waiting_ready()

print(swift.set_fans(on=True))

target_temperature = 200
print(swift.set_temperature(temperature=200, block=False))

current_temperature = 0.0
while current_temperature < target_temperature:
    ret = swift.get_temperature()
    current_temperature = ret['current_temperature']
    print(current_temperature)
    time.sleep(1)

count = 5
while count:
    swift.set_3d_feeding(distance=-5, speed=1000, relative=True, timeout=60)
    count -= 1

swift.flush_cmd()
swift.disconnect()
