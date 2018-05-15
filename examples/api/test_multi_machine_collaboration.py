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

# swift1.reset()
# swift2.reset()

swift_list = [swift1, swift2]


def multi_swift_cmd(cmd, *args, **kwargs):
    wait = kwargs.pop('wait', False)
    timeout = kwargs.get('timeout', None)
    for swift in swift_list:
        swift_cmd = getattr(swift, cmd)
        swift_cmd(*args, **kwargs, wait=False)
    if wait:
        for swift in swift_list:
            swift.flush_cmd(timeout)

print('reset')
multi_swift_cmd('reset', wait=True, speed=10000)
print('set position')
# multi_swift_cmd('set_position', x=200, y=100, z=100, speed=3000, wait=True)
# print('==============')


while True:
    multi_swift_cmd('set_position', x=200, y=0, z=100, speed=10000, wait=True, timeout=30)
    multi_swift_cmd('set_position', x=200, y=100, z=100, speed=10000, wait=True, timeout=30)
    multi_swift_cmd('set_position', x=200, y=-100, z=100, speed=10000, wait=True, timeout=30)
    multi_swift_cmd('set_position', x=200, y=0, z=150, speed=10000, wait=True, timeout=30)

