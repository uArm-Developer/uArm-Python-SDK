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

# logger.setLevel(logger.VERBOSE)


def test_callback(ret):
    print('callback:', ret)

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

while not swift.power_status:
    time.sleep(0.1)

# print('thread count:', len(threading.enumerate()))
print(swift.get_device_info())
#
#
# print(swift.get_mode())
# print(swift.set_mode(0))
# print(swift.get_mode())

# print(swift.get_position(wait=False, callback=test_callback))
# print(swift.get_polar())


# swift.set_position(x=200, wait=True, speed=10000)
# swift.set_position(y=100)
# swift.set_position(z=150, wait=True)

swift.reset(speed=1000)
print(swift.get_polar())
# swift.set_polar(stretch=200, rotation=0, height=160)

# print(swift.get_servo_angle())

# print(swift.set_servo_angle(0, 90))
# print(swift.set_wrist(angle=90, wait=False, callback=test_callback))

# swift.set_buzzer(frequency=1000, duration=3)

# print(swift.set_pump(True))
# time.sleep(1)
# print(swift.set_pump(False))

# print(swift.set_gripper(True))
# time.sleep(3)
# print(swift.set_gripper(False))

# print(swift.get_gripper_catch())
# print(swift.set_gripper(True, wait=True))
# print(swift.get_gripper_catch())

# print(swift.get_limit_switch())

# print(swift.get_servo_attach(0))
# # swift.set_servo_detach(wait=False, callback=test_callback)
# print(swift.set_servo_detach())
# print(swift.get_servo_attach(0))
# time.sleep(5)
# # swift.set_servo_attach(wait=False, callback=test_callback)
# print(swift.set_servo_attach())
# print(swift.get_servo_attach(0))


# print(swift.get_digital(1))
# print(swift.get_analog(3))

# swift.reset(speed=5000)

while True:
    time.sleep(0.5)
