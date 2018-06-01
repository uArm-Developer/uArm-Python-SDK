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
from uarm.tools.list_ports import get_ports


"""
connnect all filter uArm, and enforce sync move
"""

swift_list = []
ports = get_ports(filters={'hwid': 'USB VID:PID=2341:0042'})
for port in ports:
    swift_list.append(SwiftAPI(port=port['device']))

for swift in swift_list:
    swift.waiting_ready()
    device_info = swift.get_device_info()
    print(swift.port, device_info)
    firmware_version = device_info['firmware_version']
    if firmware_version and not firmware_version.startswith(('0.', '1.', '2.', '3.')):
        swift.set_speed_factor(0.00001)


def multi_swift_cmd(cmd, *args, **kwargs):
    wait = kwargs.pop('wait', False)
    timeout = kwargs.get('timeout', None)
    for swift in swift_list:
        if swift.connected:
            swift_cmd = getattr(swift, cmd)
            swift_cmd(*args, **kwargs, wait=False)
    if wait:
        for swift in swift_list:
            if swift.connected:
                swift.flush_cmd(timeout, wait_stop=True)
    time.sleep(0.001)

speed = 1000000
timeout = 30

while True:
    multi_swift_cmd('set_position', x=300, y=0, z=150, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi_swift_cmd('set_position', x=200, y=100, z=100, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi_swift_cmd('set_position', x=200, y=-100, z=100, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi_swift_cmd('set_position', x=200, y=0, z=150, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)





