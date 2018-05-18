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

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, cmd_pend_size=2)

swift.waiting_ready()

print(swift.get_device_info())

swift.set_mode(0)

speed = 1000000

# swift.reset(speed=speed)

while swift.connected:
    swift.set_position(x=300, y=0, z=150, speed=speed)
    swift.set_position(z=50)
    swift.set_position(z=150)
    swift.set_position(x=200, y=100, z=100)
    swift.set_position(z=50)
    swift.set_position(z=150)
    swift.set_position(x=200, y=0, z=150)
    swift.set_position(z=50)
    swift.set_position(z=150)

    swift.set_polar(stretch=150, rotation=90, height=150, speed=speed)
    swift.set_polar(stretch=150, rotation=45, height=150, speed=speed)
    swift.set_polar(stretch=150, rotation=135, height=150, speed=speed)

    swift.set_polar(stretch=150, rotation=135, height=90, speed=speed)
    swift.set_polar(stretch=150, rotation=135, height=200, speed=speed)
    swift.set_polar(stretch=150, rotation=135, height=150, speed=speed)

    swift.set_polar(stretch=150, rotation=135, height=150, speed=speed)
    swift.set_polar(stretch=200, rotation=135, height=150, speed=speed)


