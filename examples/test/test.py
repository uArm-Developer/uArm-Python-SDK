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
from uarm.wrapper.metal_api import MetalAPI

metal = MetalAPI(filters={'hwid': 'USB VID:PID=0403:6001'})
metal.waiting_ready()


device_info = metal.get_device_info()
print(device_info)


# def test(ret):
#     print(ret)
#
# print(metal.send_cmd_sync('G0'))
# metal.send_cmd_async('G0', callback=test)

while True:
    time.sleep(1)

