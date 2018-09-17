#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFactory, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

# import os
# import sys
# import time
# sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
# from uarm.wrapper import SwiftAPI
# from uarm.utils.log import logger
#
# logger.setLevel(logger.VERBOSE)
#
#
# swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, callback_thread_pool_size=1)
# swift.waiting_ready()
#
#
# device_info = swift.get_device_info()
# print(device_info)
#
# swift.set_position(x=200, y=0, z=100)
# time.sleep(5)
# print(swift.get_polar())
#
#
# # # def test(ret):
# # #     print(ret)
# # #
# # # print(metal.send_cmd_sync('G0'))
# # # metal.send_cmd_async('G0', callback=test)
# #
# # while True:
# #     time.sleep(1)

import time
from serial import Serial

com = Serial("COM12", baudrate=115200)

print('getCD:', com.getCD())
print('getCTS:', com.getCTS())
print('getDSR:', com.getDSR())
print('getRI:', com.getRI())
print('get_settings:', com.get_settings())
print('timeout:', com.timeout)

while True:
    time.sleep(1)

