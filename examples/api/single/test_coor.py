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
import functools
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI

"""
api test: coordinate convert
"""

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

swift.waiting_ready()
time.sleep(2)

pos = [180, 0, 150]
if swift.check_pos_is_limit(pos) is False:
    ret = swift.coordinate_to_angles(*pos)
    if isinstance(ret, list):
        print('coor to angles: {} ==> {}'.format(pos, ret))
        _ret = swift.angles_to_coordinate(ret)
        if isinstance(ret, list):
            print('angles to coor: {} ==> {}'.format(ret, _ret))
        else:
            print('ngles to coor failed')
    else:
        print('coor to angles failed')
else:
    print('pos: {} is limit'.format(pos))

pos = [100, 0, 150]
if swift.check_pos_is_limit(pos) is False:
    ret = swift.coordinate_to_angles(*pos)
    if isinstance(ret, list):
        print('coor to angles: {} ==> {}'.format(pos, ret))
        _ret = swift.angles_to_coordinate(ret)
        if isinstance(ret, list):
            print('angles to coor: {} ==> {}'.format(ret, _ret))
        else:
            print('ngles to coor failed')
    else:
        print('coor to angles failed')
else:
    print('pos: {} is limit'.format(pos))

swift.flush_cmd()
swift.disconnect()

