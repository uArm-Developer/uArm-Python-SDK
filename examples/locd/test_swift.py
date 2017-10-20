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
from uf.swift.swift_via_cdbus2raw import Swift
from uf.utils.log import *

#logger_init(logging.VERBOSE)
logger_init(logging.DEBUG)
#logger_init(logging.INFO)


ufc = ufc_init()

print('setup locd net ...')

lo_dev_iomap = {
        'lo_service': 'lo_service',
        'RV_socket':  'cdbus2raw_RV',
        'RA_socket':  'cdbus2raw_RA',
        'SA2000_rpt': 'cdbus2raw_SA'
}

lo_dev = LocdViaUart2Cdbus(ufc, 'locd_via_uart2cdbus', lo_dev_iomap)
              #filters = {'hwid': 'LOCATION=1-6.1'})


print('setup swift ...')

swift_iomap = {
        'cdbus2raw':  'cdbus2raw',
        'pos_in':     'swift_pos_in',
        'pos_out':    'swift_pos_out',
        'ptc':        'swift_ptc',
        'service':    'swift_service',
        
        'lo_service':   'lo_service',
        'cdbus2raw_RV': 'cdbus2raw_RV',
        'cdbus2raw_RA': 'cdbus2raw_RA',
        'cdbus2raw_SA': 'cdbus2raw_SA'
}

swift = Swift(ufc, 'swift', swift_iomap, listen_port = 2000)
              #dev_filter = 'M: cdbus2raw; S: 13ffc6604374634355832175')


print('setup test ...')

def pos_cb(msg):
    print('pos_cb: ' + msg)

test_ports = {
        'cdbus2raw': {'dir': 'out', 'type': 'service'},
        'swift_pos':     {'dir': 'out', 'type': 'topic'},
        'swift_pos_out': {'dir': 'in',  'type': 'topic', 'callback': pos_cb},
        'swift_ptc':     {'dir': 'out', 'type': 'service'},
        'swift_service': {'dir': 'out', 'type': 'service'}
}

test_iomap = {
        'cdbus2raw':     'cdbus2raw',
        'swift_pos':     'swift_pos_in',
        'swift_pos_out': 'swift_pos_out',
        'swift_ptc':     'swift_ptc',
        'swift_service': 'swift_service'
}

# install handle for ports which are listed in the iomap
ufc.node_init('test', test_ports, test_iomap)

while True:
    ret = test_ports['cdbus2raw']['handle'].call('get state')
    if ret == 'ok, CONFIGURED':
        print('cdbus2raw ready...')
        break
    sleep(1)

#print('enable report_pos: ' + test_ports['swift_service']['handle'].call('set report_pos on 0.2'))
#print('disable report_pos: ' + test_ports['swift_service']['handle'].call('set report_pos off'))

print('set X330 ...')
# topics are always async
# without 'G0', port 'pos' is dedicated for moving
test_ports['swift_pos']['handle'].publish('_T20 X350 Y0 Z50')
test_ports['swift_ptc']['handle'].call('set flush') # wait for first command send out


print('ret1: ' + test_ports['swift_service']['handle'].call('set cmd_sync _T10 G0 X340'))
print('ret2: ' + test_ports['swift_service']['handle'].call('set cmd_sync _T10 G0 X320'))
print('ret3: ' + test_ports['swift_service']['handle'].call('set cmd_sync _T10 G0 X300'))
print('ret4: ' + test_ports['swift_service']['handle'].call('set cmd_sync _T10 G0 X200'))
print('ret5: ' + test_ports['swift_service']['handle'].call('set cmd_sync _T10 G0 X190'))

print('done ...')
while True:
    sleep(1)

