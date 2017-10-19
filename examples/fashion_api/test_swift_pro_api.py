#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import sys, os
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from uf.wrapper.swift_api import SwiftAPI
from uf.utils.log import *

#logger_init(logging.VERBOSE)
#logger_init(logging.DEBUG)
logger_init(logging.INFO)

print('setup swift ...')

#swift = SwiftAPI(dev_port = '/dev/ttyACM0')
#swift = SwiftAPI(filters = {'hwid': 'USB VID:PID=2341:0042'})
swift = SwiftAPI() # default by filters: {'hwid': 'USB VID:PID=2341:0042'}


print('sleep 2 sec ...')
sleep(2)

print('device info: ')
print(swift.get_device_info())

print('\nset X350 Y0 Z50 F1500 ...')

swift.set_position(350, 0, 50, speed = 1500, timeout = 20)
swift.flush_cmd() # avoid follow 5 command timeout

print('set X340 ...')
swift.set_position(x = 340)
print('set X320 ...')
swift.set_position(x = 320)
print('set X300 ...')
swift.set_position(x = 300)
print('set X200 ...')
swift.set_position(x = 200)
print('set X190 ...')
swift.set_position(x = 190)

# wait all async cmd return before send sync cmd
swift.flush_cmd()

print('set Z100 ...')
swift.set_position(z = 100, wait = True)
print('set Z150 ...')
swift.set_position(z = 150, wait = True)

swift.set_buzzer()

print('done ...')
while True:
    sleep(1)

