#!/usr/bin/env python3
from __future__ import print_function
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


# import _thread, threading
# import serial
import sys, os
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from __init__ import SERIAL_PORT
from uf.wrapper.swift_api import SwiftAPI
from uf.utils.log import logger_init, logging

#logger_init(logging.VERBOSE)
#logger_init(logging.DEBUG)
logger_init(logging.INFO)

def main():
    print('setup swift ...')

    swift = SwiftAPI(dev_port=SERIAL_PORT)

    print('sleep 2 sec ...')
    sleep(2)

    print('device info: ')
    print(swift.get_device_info())

    movements = [
        {'x':200, 'y':0, 'z':50, 'speed':500},
        {'z':100, 'speed':1000},
        {'z':50, 'speed':1000},
        {'z':100, 'speed':1500},
        {'z':50, 'speed':1500},
        {'z':100, 'speed':2000},
        {'z':50, 'speed':2000},
        {'z':100, 'speed':2500},
        {'z':50, 'speed':2500},
        {'z':100, 'speed':3000},
        {'z':50, 'speed':3000},
        {'z':100, 'speed':3500},
        {'z':50, 'speed':3500},
        {'z':100, 'speed':4000},
        {'z':50, 'speed':4000},
        {'z':100, 'speed':4500},
        {'z':50, 'speed':4500},
        {'z':100, 'speed':5000},
        {'z':50, 'speed':5000},
    ]

    for movement in movements:
        print('\nset ' + ' '.join([
            "%s%d" % (key.upper(), value) for key, value in movement.items()
        ]))
        swift.set_position(**movement)
        sleep(0.1)
        while swift.get_is_moving():
            sleep(0.1)
        swift.set_buzzer()

    print('done ...')
    while True:
        sleep(1)

if __name__ == '__main__':
    main()
