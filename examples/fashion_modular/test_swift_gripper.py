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

from uf.ufc import ufc_init
from uf.swift import Swift
from uf.utils.log import *

logger_init(logging.DEBUG)

print('setup swift ...')

swift_iomap = {
        'pos_in':  'swift_pos_in',
        'service': 'swift_service',
        'gripper': 'swift_gripper'
}

ufc = ufc_init()
swift = Swift(ufc, 'swift', swift_iomap)


print('setup test ...')

test_ports = {
        'swift_pos':     {'dir': 'out', 'type': 'topic'},
        'swift_service': {'dir': 'out', 'type': 'service'},
        'swift_gripper': {'dir': 'out', 'type': 'service'}
}

test_iomap = {
        'swift_pos':     'swift_pos_in',
        'swift_service': 'swift_service',
        'swift_gripper': 'swift_gripper'
}

# install handle for ports which are listed in the iomap
ufc.node_init('test', test_ports, test_iomap)


print('sleep 2 sec ...')
sleep(2)


print('set X190: ' + test_ports['swift_service']['handle'].call('set cmd_sync _T20 G0 X190 Z50'))

# FIXME: 'set on' always timeout according to firmware's bug
print('gripper set on return: ' + test_ports['swift_gripper']['handle'].call('set value on'))
print('gripper get state return: ' + test_ports['swift_gripper']['handle'].call('get value'))

print('gripper set off return: ' + test_ports['swift_gripper']['handle'].call('set value off'))
print('gripper get state return: ' + test_ports['swift_gripper']['handle'].call('get value'))

print('done ...')
while True:
    sleep(1)

