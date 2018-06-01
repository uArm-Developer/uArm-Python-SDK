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
api test: send cmd
"""

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

swift.waiting_ready()
device_info = swift.get_device_info()
print(device_info)
firmware_version = device_info['firmware_version']
if firmware_version and not firmware_version.startswith(('0.', '1.', '2.', '3.')):
    swift.set_speed_factor(0.00005)


swift.send_cmd_sync('G0 X200 Y0 Z100 F5000')
swift.send_cmd_async('M2210 F1000 T2000')
swift.send_cmd_async('M2231 V1')
print(swift.send_cmd_sync('M106', no_cnt=True))
time.sleep(2)
swift.send_cmd_async('M2231 V0')

print('pos:', swift.send_cmd_sync('P2220'))

swift.flush_cmd()
swift.disconnect()
