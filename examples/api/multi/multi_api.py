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
from uarm.swift.multi import MultiSwiftAPI
from uarm.tools.list_ports import get_ports


"""
MultiSwiftAPI 测试， 测试版（不建议使用，尚未加入到正式API，可能会去除）
"""

swift_list = []
ports = get_ports(filters={'hwid': 'USB VID:PID=2341:0042'})
for port in ports:
    swift_list.append(SwiftAPI(port=port['device']))

speed = 1000000
timeout = 30

multi = MultiSwiftAPI(swift_list)
# multi.multi_reset(speed=speed)

while True:
    multi.multi_cmd_sync('set_position', x=300, y=0, z=150, speed=speed, wait=True, timeout=timeout)
    multi.multi_cmd_sync('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi.multi_cmd_sync('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi.multi_cmd_sync('set_position', x=200, y=100, z=100, speed=speed, wait=True, timeout=timeout)
    multi.multi_cmd_sync('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi.multi_cmd_sync('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi.multi_cmd_sync('set_position', x=200, y=-100, z=100, speed=speed, wait=True, timeout=timeout)
    multi.multi_cmd_sync('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi.multi_cmd_sync('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi.multi_cmd_sync('set_position', x=200, y=0, z=150, speed=speed, wait=True, timeout=timeout)
    multi.multi_cmd_sync('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi.multi_cmd_sync('set_position', z=150, speed=speed, wait=True, timeout=timeout)





