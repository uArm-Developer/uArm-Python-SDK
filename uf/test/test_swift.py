#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import _thread, threading
import serial
import sys, os
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from uf.ufc import ufc_init
from uf.swift import Swift
from uf.utils.log import *

logger_init(logging.DEBUG)

print('setup swift ...')

swift_iomap = {
        'pos_in': '/swift_pos_in',
        'service': '/swift_service'
}

ufc = ufc_init()
swift = Swift(ufc, 'swift', swift_iomap, '/dev/ttyACM0', 115200)


print('setup test ...')

test_ports = {
        'swift_pos': {'dir': 'out', 'type': 'topic'},
        'swift_service': {'dir': 'out', 'type': 'service'}
}

test_iomap = {
        'swift_pos': '/swift_pos_in',
        'swift_service': '/swift_service'
}

# install handle for ports which are listed in the iomap
ufc.node_init('test', test_ports, test_iomap)


print('sleep 2 sec ...')
sleep(2)


print('set X330 ...')
# topics are always async
# without 'G0', port 'pos' is dedicated for moving
test_ports['swift_pos']['handle'].publish('X350 Y0 Z50')


print('ret1: ' + test_ports['swift_service']['handle'].call('set command G0 X340'))
print('ret2: ' + test_ports['swift_service']['handle'].call('set command G0 X320'))
print('ret3: ' + test_ports['swift_service']['handle'].call('set command G0 X300'))
print('ret4: ' + test_ports['swift_service']['handle'].call('set command G0 X200'))
print('ret5: ' + test_ports['swift_service']['handle'].call('set command G0 X190'))

print('done ...')
while True:
    sleep(1)

