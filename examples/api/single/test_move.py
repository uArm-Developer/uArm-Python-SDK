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
测试有关移动的接口
"""

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

swift.waiting_ready()

swift.set_position(x=200, speed=10000)
swift.set_position(y=100)
swift.set_position(z=100)
swift.flush_cmd()

swift.set_polar(stretch=160, speed=5000)
swift.set_polar(rotation=120)
swift.set_polar(height=150)
print(swift.set_polar(stretch=150, rotation=90, height=150, wait=True))

swift.flush_cmd()

time.sleep(10)
swift.disconnect()
