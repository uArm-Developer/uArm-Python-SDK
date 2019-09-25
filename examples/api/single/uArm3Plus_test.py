#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFactory, Inc.
# All rights reserved.
#
#

import os
import sys
import time
import functools

import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, enable_handle_thread=False)
# swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, enable_write_thread=True)
# swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, enable_report_thread=True)
# swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, enable_handle_thread=True, enable_write_thread=True, enable_report_thread=True)

swift.waiting_ready() # wait the rebot ready
print(swift.get_device_info())


move_speed = 100

time.sleep(5)                                       # <! must wait the effector check itself
rtn = swift.get_mode(wait=True,timeout=10)          # <! make sure the work mode is 5
print( rtn )
if rtn != 5:
    swift.set_mode(5)
    time.sleep(5)                                   # <! must wait the effector check itself


swift.set_position(x=150,y=150,z=150,speed=move_speed,wait=True,timeout=10,cmd='G0')
# print( swift.get_position() )
# print( swift.get_servo_angle() )
# print( swift.send_cmd_sync('P2243') )

while True:
    swift.set_position(x=400,y=0,z=50,speed=move_speed,wait=True,timeout=10,cmd='G0')
    time.sleep(0.5)
    swift.set_position(y=-250, speed=move_speed, wait=True, timeout=10, cmd='G0')
    time.sleep(0.5)
    swift.set_position(y=0, speed=move_speed, wait=True, timeout=10, cmd='G0')
    time.sleep(0.5)
    swift.set_position(y=250 ,speed=move_speed, wait=True, timeout=10, cmd='G0')
    time.sleep(0.5)
    swift.set_position(z=250, speed=move_speed, wait=True, timeout=10, cmd='G0')
    time.sleep(0.5)
    swift.set_position(y=-250, speed=move_speed, wait=True, timeout=10, cmd='G0')
    time.sleep(0.5)
    swift.set_position(y=0, speed=move_speed, wait=True, timeout=10, cmd='G0')
    time.sleep(0.5)
    swift.set_position(y=250, speed=move_speed, wait=True, timeout=10, cmd='G0')

    swift.set_position(x=325.5, y=0, z=411.5, speed=move_speed, wait=True, timeout=10, cmd='G0')
    time.sleep(0.5)

    swift.set_servo_angle(servo_id=3, angle=30)
    time.sleep(5)                                       # <!  wait the effector work done
    swift.set_servo_angle(servo_id=3, angle=150)
    time.sleep(5)                                       # <!  wait the effector work done

