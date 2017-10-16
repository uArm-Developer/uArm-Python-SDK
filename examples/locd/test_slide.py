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
from uf.comm.locd_via_uart2cdbus import LocdViaUart2Cdbus
from uf.accessories.linear_motion import LinearMotion
from uf.utils.log import *

logger_init(logging.VERBOSE)
#logger_init(logging.DEBUG)
#logger_init(logging.INFO)


ufc = ufc_init()

print('setup locd net ...')

lo_dev_iomap = {
        'lo_service': 'lo_service',
        'RV_socket':  'linear_motion_RV',
        'RA_socket':  'linear_motion_RA'
}

lo_dev = LocdViaUart2Cdbus(ufc, 'locd_via_uart2cdbus', lo_dev_iomap)
              #filters = {'hwid': 'LOCATION=1-6.1'})


print('setup linear_motion ...')

linear_motion_iomap = {
        'service':    'linear_motion',
        
        'lo_service': 'lo_service',
        'RV_socket':  'linear_motion_RV',
        'RA_socket':  'linear_motion_RA'
}

linear_motion = LinearMotion(ufc, 'linear_motion', linear_motion_iomap)
              #dev_filter = 'M: uf_slide; S: xxxxxxxxxxxxxxxxxxxxxxx')


print('setup test ...')

test_ports = {
        'linear_motion': {'dir': 'out', 'type': 'service'}
}

test_iomap = {
        'linear_motion': 'linear_motion'
}

# install handle for ports which are listed in the iomap
ufc.node_init('test', test_ports, test_iomap)

while True:
    ret = test_ports['linear_motion']['handle'].call('get state')
    if ret.startswith('ok, CONFIGURED'):
        print('device ready...')
        break
    sleep(1)

print('get pos: ', test_ports['linear_motion']['handle'].call('get pos'))
print('test move: ', test_ports['linear_motion']['handle'].call('set pos 200 200'))
print('get pos: ', test_ports['linear_motion']['handle'].call('get pos'))
print('test move: ', test_ports['linear_motion']['handle'].call('set pos 50 200'))
print('get pos: ', test_ports['linear_motion']['handle'].call('get pos'))


print('done ...')
while True:
    sleep(1)

