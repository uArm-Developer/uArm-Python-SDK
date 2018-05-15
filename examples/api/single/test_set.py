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
测试部分有关设置的接口
"""

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

swift.waiting_ready()


swift.set_buzzer(frequency=1000, duration=2, wait=True)
swift.set_pump(on=True)
time.sleep(2)
swift.set_pump(False)

swift.set_gripper(catch=True)
time.sleep(2)
swift.set_gripper(catch=False)

swift.flush_cmd()
swift.disconnect()
