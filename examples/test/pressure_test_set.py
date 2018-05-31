#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFactory, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from uarm.wrapper import SwiftAPI

"""
pressure test: set mode
"""

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, cmd_pend_size=2)

swift.waiting_ready()

print(swift.get_device_info())

mode = swift.get_mode()
print('mode:', mode)

mode_count = 4

count = 1
while swift.connected:
    mode = (mode + 1) % mode_count
    if swift.set_mode(mode) != mode:
        print('set mode {} failed, count={}'.format(mode, count))
    count += 1
    if count == 1000000:
        count = 1
