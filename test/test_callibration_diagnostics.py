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
from collections import OrderedDict

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from __init__ import SERIAL_PORT
from uf.wrapper.swift_api import SwiftAPI
from uf.utils.log import logger_init, logging

#logger_init(logging.VERBOSE)
#logger_init(logging.DEBUG)
logger_init(logging.INFO)

def send_cmd_sync_ok(swift, command):
    response = swift.send_cmd_sync(command)
    assert response.startswith("ok"), \
        "command \"%s\" failed: %s" % (command, response)
    return response

def main():
    print('setup swift ...')

    swift = SwiftAPI(dev_port=SERIAL_PORT)

    print('sleep 2 sec ...')
    sleep(2)

    print('device info: ')
    print(swift.get_device_info())

    print('EEPROM Values: ')
    print('-> reference_angle_value:')
    # define EEPROM_ON_CHIP                 0
    # define EEPROM_REFERENCE_VALUE_ADDR    800
    # define DATA_TYPE_INTEGER              2
    #
    # reference_angle_value[X_AXIS] = getE2PROMData(EEPROM_ON_CHIP, EEPROM_REFERENCE_VALUE_ADDR, DATA_TYPE_INTEGER);
	# reference_angle_value[Y_AXIS] = getE2PROMData(EEPROM_ON_CHIP, EEPROM_REFERENCE_VALUE_ADDR+2, DATA_TYPE_INTEGER);
	# reference_angle_value[Z_AXIS] = getE2PROMData(EEPROM_ON_CHIP, EEPROM_REFERENCE_VALUE_ADDR+4, DATA_TYPE_INTEGER);	
    reference_angle_value = []
    reference_angle_value.append(send_cmd_sync_ok(swift, 'M2211 N0 A800 T2'))
    reference_angle_value.append(send_cmd_sync_ok(swift, 'M2211 N0 A802 T2'))
    reference_angle_value.append(send_cmd_sync_ok(swift, 'M2211 N0 A804 T2'))
    print(reference_angle_value)
    
    print("-> height offset:")
    
    # define EEPROM_HEIGHT_ADDR	    910
    # define DATA_TYPE_FLOAT        4
    # getE2PROMData(EEPROM_ON_CHIP, EEPROM_HEIGHT_ADDR, DATA_TYPE_FLOAT);
    height_offset = send_cmd_sync_ok(swift, "M2211 N0 A910 T4")
    print(height_offset)
    
    print("-> front offset:")
    # define EEPROM_FRONT_ADDR      920
    # getE2PROMData(EEPROM_ON_CHIP, EEPROM_FRONT_ADDR, DATA_TYPE_FLOAT);
    front_offset = send_cmd_sync_ok(swift, "M2211 N0 A920 T4")
    print(front_offset)

    # print('resetting...')
    # swift.reset()

    swift.set_servo_detach(2, wait=True)
    sleep(1)
    swift.set_servo_detach(1, wait=True)
    
    print("now you can position the arm on the X-Z plane (rotation locked at zero)")

    while True:
        sleep(1)
        raw_in = input("Press enter to get calibration data, r to set reference, h to zero height, ... ")
        # swift.set_servo_attach(wait=True)
        # print("get_position: %s" % swift.get_position())

        # hack to update current position on device
        send_cmd_sync_ok(swift, "M2400 S1")

        values = OrderedDict()

        # Raw sensor values
        response = send_cmd_sync_ok(swift, "P2242")
        values['sensor'] = OrderedDict([
            (token[0], token[1:]) for token in response.split(" ")[1:]
        ])

        # Cartesian coordinates
        response = send_cmd_sync_ok(swift, "P2220")
        values['cartesian'] = OrderedDict([
            (token[0], token[1:]) for token in response.split(" ")[1:]
        ])

        # angle values
        values['angle'] = OrderedDict()
        for index, name in [
                (0, 'B'),
                (1, 'L'),
                (2, 'R')
        ]:
            response = send_cmd_sync_ok(swift, "P2206 N%s" % index)
            values['angle'][name] = response.split(" ")[1][1:]

        print("; ".join([
            ", ".join([
                "%s:%+07.2f" % (key, float(value)) for key, value in values[dictionary].items()
            ]) for dictionary in ['sensor', 'cartesian', 'angle']
        ]))

        if raw_in == "s":
            print("M2401: %s" % swift.send_cmd_sync("M2401 V22765"))
        elif raw_in == "h":
            print("M2410: %s" % swift.send_cmd_sync("M2410"))

        # swift.set_buzzer()
        # swift.set_servo_detach(wait=True)

    print('done ...')
    while True:
        sleep(1)

if __name__ == '__main__':
    main()
