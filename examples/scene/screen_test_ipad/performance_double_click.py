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
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI
from uarm.tools.list_ports import get_ports

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

swift.waiting_ready(timeout=3)

device_info = swift.get_device_info()
print(device_info)
firmware_version = device_info['firmware_version']
#if firmware_version and not firmware_version.startswith(('0.', '1.', '2.', '3.')):
#    swift.set_speed_factor(0.0005)

swift.set_mode(0)

while True:
    swift.set_position(x=170,y=0,z=12,speed=200,cmd='G0')
    swift.set_position(x=170,y=0,z=18,speed=200,cmd='G0')
    swift.set_position(x=170,y=0,z=12,speed=200,cmd='G0')
    swift.set_position(x=170,y=0,z=18,speed=200,cmd='G0')
    time.sleep(2)