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


#
# swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, callback_thread_pool_size=1)
# swift.waiting_ready()
#
#
# device_info = swift.get_device_info()
# print(device_info)
#
#
# # def test(ret):
# #     print(ret)
# #
# # print(metal.send_cmd_sync('G0'))
# # metal.send_cmd_async('G0', callback=test)
#
# while True:
#     time.sleep(1)

