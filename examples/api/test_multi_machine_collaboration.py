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

from uarm.wrapper import SwiftAPI

swift1 = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})
swift2 = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

time.sleep(2)

swift1.reset()
swift2.reset()

swift_list = [swift1, swift2]

def multi_swift_cmd(cmd, *args, **kwargs):
    for swift in swift_list:
        cmd = getattr(swift, cmd)
        break
    for swift in swift_list:
        cmd(*args, **kwargs)

while True:
    swift1.set_position(X=200, Y=0, Z=100, speed=5000)
    swift1.set_position(X=200, Y=0, Z=100, speed=5000)

