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
api test: set
"""

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

swift.waiting_ready()


swift.set_buzzer(frequency=1000, duration=2, wait=True)
print(swift.set_pump(on=True))
time.sleep(2)
print(swift.set_pump(on=False))

print(swift.set_gripper(catch=True))
time.sleep(2)
print(swift.set_gripper(catch=False))

time.sleep(4)
swift.flush_cmd()
swift.disconnect()
