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


speed_s = 100
delay = 1

while True:
    cmd_s = 'G0'
    swift.set_position(x=210,y=0,z=30,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=166,y=109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=166,y=109,z=8,speed=speed_s,cmd=cmd_s)
    time.sleep(0.5)
    swift.set_position(x=166,y=109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)

    swift.set_position(x=210,y=0,z=30,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=313,y=109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=313,y=109,z=5,speed=speed_s,cmd=cmd_s)
    time.sleep(0.5)
    swift.set_position(x=313,y=109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)

    swift.set_position(x=210,y=0,z=30,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=313,y=-109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=313,y=-109,z=5,speed=speed_s,cmd=cmd_s)
    time.sleep(0.5)
    swift.set_position(x=313,y=-109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)

    swift.set_position(x=210,y=0,z=30,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=166,y=-109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=166,y=-109,z=5,speed=speed_s,cmd=cmd_s)
    time.sleep(0.5)
    swift.set_position(x=166,y=-109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)

    swift.set_position(x=210,y=0,z=30,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)

    cmd_s = 'G1'
    swift.set_position(x=166,y=109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=313,y=109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=313,y=-109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=166,y=-109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=166,y=0,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)
    swift.set_position(x=166,y=109,z=20,speed=speed_s,cmd=cmd_s)
    time.sleep(delay)

    swift.set_position(x=210, y=0, z=30, speed=speed_s, cmd=cmd_s)
    time.sleep(delay)