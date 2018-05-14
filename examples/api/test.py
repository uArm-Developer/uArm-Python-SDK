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
from uarm.utils.log import logger

logger.setLevel(logger.VERBOSE)


swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

time.sleep(2)

print('thread count:', len(threading.enumerate()))
print(swift.get_device_info())
print('thread count:', len(threading.enumerate()))

time.sleep(5)
print('thread count:', len(threading.enumerate()))
swift.disconnect()
print('thread count:', len(threading.enumerate()))
time.sleep(1)
print('thread count:', len(threading.enumerate()))

while True:
    time.sleep(1)
