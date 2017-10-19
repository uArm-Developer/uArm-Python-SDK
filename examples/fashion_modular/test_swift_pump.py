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


#logger_init(logging.VERBOSE)
logger_init(logging.INFO)
ufc = ufc_init()


print('setup swift ...')
swift_iomap = {
        'pos_in':       'swift_pos_in',
        'service':      'swift_service',
        'pump':         'swift_pump',
        'limit_switch': 'limit_switch'
}
swift = Swift(ufc, 'swift', swift_iomap)


print('setup test ...')

def limit_switch_cb(msg):
    print('limit_switch state: ' + msg)

test_ports = {
        'swift_pos':     {'dir': 'out', 'type': 'topic'},
        'swift_service': {'dir': 'out', 'type': 'service'},
        'swift_pump':    {'dir': 'out', 'type': 'service'},
        'limit_switch':  {'dir': 'in',  'type': 'topic', 'callback': limit_switch_cb},
}
test_iomap = {
        'swift_pos':     'swift_pos_in',
        'swift_service': 'swift_service',
        'swift_pump':    'swift_pump',
        'limit_switch':  'limit_switch'
}
# install handle for ports which are listed in the iomap
ufc.node_init('test', test_ports, test_iomap)


print('sleep 2 sec ...')
sleep(2)

print('get dev_info return: ' + test_ports['swift_service']['handle'].call('get dev_info'))

# send arbitrary command
print('set X190: ' + test_ports['swift_service']['handle'].call('set cmd_sync _T20 G0 X190 Z50'))

# FIXME: 'set on' never timeout according to the firmware or hardware
print('pump set on return: ' + test_ports['swift_pump']['handle'].call('set value on'))
print('pump get state return: ' + test_ports['swift_pump']['handle'].call('get value'))

print('pump set off return: ' + test_ports['swift_pump']['handle'].call('set value off'))
print('pump get state return: ' + test_ports['swift_pump']['handle'].call('get value'))

print('get limit_switch return: ' + test_ports['swift_pump']['handle'].call('get limit_switch'))


print('done ...')
while True:
    sleep(1)

