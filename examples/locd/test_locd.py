#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import sys, os
from time import sleep
import capnp

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from uf.ufc import ufc_init
from uf.comm.locd import locd_capnp
from uf.comm.locd_via_uart2cdbus import LocdViaUart2Cdbus
from uf.utils.log import *

logger_init(logging.VERBOSE)
#logger_init(logging.DEBUG)
#logger_init(logging.INFO)

print('setup LocdViaUart2Cdbus ...')

locd_via_uart2cdbus_iomap = {
        'lo_service':           'lo_service',
        'lo_up2down_repl_src':  'lo_up2down_repl_src',
        'lo_down2up':           'lo_down2up'
}

ufc = ufc_init()
locd_via_uart2cdbus = LocdViaUart2Cdbus(ufc, 'locd_via_uart2cdbus', locd_via_uart2cdbus_iomap)
# filters = {'hwid': 'LOCATION=2-2'}


print('setup test ...')

def lo_down2up_cb(msg):
    packet = locd_capnp.LoCD.from_bytes_packed(msg)
    print('test: lo_down2up_cb: ', packet)

test_ports = {
        'lo_service':           {'dir': 'out', 'type': 'service'},
        'lo_up2down_repl_src':  {'dir': 'out', 'type': 'topic'},
        'lo_down2up':           {'dir': 'in',  'type': 'topic',
                                 'callback': lo_down2up_cb, 'data_type': bytes}
}

test_iomap = {
        'lo_service':           'lo_service',
        'lo_up2down_repl_src':  'lo_up2down_repl_src',
        'lo_down2up':           'lo_down2up'
}

# install handle for ports which are listed in the iomap
ufc.node_init('test', test_ports, test_iomap)


print('sleep 2 sec ...')
sleep(2)

print('current mac address: ' + test_ports['lo_service']['handle'].call('get mac'))

print('done ...')
while True:
    sleep(1)

