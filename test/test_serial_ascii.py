#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import _thread, threading
import serial
import sys
from time import sleep

sys.path.append("../") # invoke current script at $pyuf/

from pyuf.ufc import ufc_init
from pyuf.comm.serial_ascii import SerialAscii

print('setup ser_ascii ...')

ser_iomap = {
        'out': '/ser_out',
        'in': '/ser_in',
        'service': '/ser_service'
}

ufc = ufc_init()
ser_ascii = SerialAscii(ufc, 'ser_ascii', ser_iomap, '/dev/ttyACM0', 115200)


print('setup test ...')

def ser_out_cb(msg):
    print('ser_out_cb: ' + msg)

test_ports = {
        'ser_out': {'dir': 'in', 'type': 'topic', 'callback': ser_out_cb},
        'ser_in': {'dir': 'out', 'type': 'topic'},
        'ser_service': {'dir': 'out', 'type': 'service'}
}

test_iomap = {
        'ser_out': '/ser_out',
        'ser_in': '/ser_in',
        'ser_service': '/ser_service'
}

ufc.node_init('test', test_ports, test_iomap)


print('\nsleep 2 sec ...\n')
sleep(2)

print('\nset X330 ...')
test_ports['ser_in']['handle'].publish('G0 X300')

print('test service ...')
print('service ret: ' + test_ports['ser_service']['handle'].call('...'))

print('done ...')
while True:
    sleep(1)

