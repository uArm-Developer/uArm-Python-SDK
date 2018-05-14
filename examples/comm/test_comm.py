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

from uarm.comm import Serial
from uarm.utils.log import logger

logger.setLevel(logger.DEBUG)

com = Serial(filters={'hwid': 'USB VID:PID=2341:0042'})
# com = Serial()
com.connect()

import threading
time.sleep(100)
print(len(threading.enumerate()))
com.disconnect()
print(len(threading.enumerate()))
time.sleep(2)
print(len(threading.enumerate()))

time.sleep(10)
