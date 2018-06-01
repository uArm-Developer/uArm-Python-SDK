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
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from uarm.wrapper import SwiftAPI

swift = SwiftAPI()
swift.waiting_ready()

device_info = swift.get_device_info()
firmware_version = device_info['firmware_version']

def test(ret):
    print(ret)

print(swift.send_cmd_sync('G0'))
swift.send_cmd_async('G0', callback=test)

while True:
    time.sleep(1)

