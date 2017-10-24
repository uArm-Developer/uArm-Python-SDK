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
from uf.comm.locd.locd_serdes import LoCD
from uf.comm.locd.locd import *
from uf.comm.locd_via_uart2cdbus import LocdViaUart2Cdbus
from uf.utils.log import *

logger_init(logging.VERBOSE)
#logger_init(logging.DEBUG)
#logger_init(logging.INFO)

print('setup LocdViaUart2Cdbus ...')

locd_via_uart2cdbus_iomap = {
        'lo_service':           'lo_service',
                                                # first field: (A: down2up; V: up2down)
        'RV_test':              'RV_test',      # RV: UDP request
        'RA_test':              'RA_test',      # RA: UDP answer
        'SA2000_rpt':           'SA2000_rpt'    # SA+num: UDP service request
}

ufc = ufc_init()
locd_via_uart2cdbus = LocdViaUart2Cdbus(ufc, 'locd_via_uart2cdbus', locd_via_uart2cdbus_iomap)
# filters = {'hwid': 'LOCATION=2-2'}


print('setup test ...')

def RA_test_cb(msg):
    packet = LoCD.from_bytes_packed(msg)
    print('RA: ', packet)

def SA2000_rpt_cb(msg):
    packet = LoCD.from_bytes_packed(msg)
    print('RPT: ', packet)

test_ports = {
        'lo_service':           {'dir': 'out', 'type': 'service'},
        'RV_test':              {'dir': 'out', 'type': 'topic'},
        'RA_test':              {'dir': 'in',  'type': 'topic',
                                 'callback': RA_test_cb, 'data_type': bytes},
        'SA2000_rpt':           {'dir': 'in',  'type': 'topic',
                                 'callback': SA2000_rpt_cb, 'data_type': bytes}
}

test_iomap = {
        'lo_service':           'lo_service',
        'RV_test':              'RV_test',
        'RA_test':              'RA_test',
        'SA2000_rpt':           'SA2000_rpt'
}

# install handle for ports which are listed in the iomap
ufc.node_init('test', test_ports, test_iomap)


print('sleep 2 sec ...')
sleep(2)

pc_mac = test_ports['lo_service']['handle'].call('get mac')
print('current mac address: ' + pc_mac)
pc_mac = int(pc_mac[-2:], 16)

print('\nsearching online devices...')
packet = LoCD.new_message()
packet.dstMac = 0xff
packet.dstAddrType = LO_ADDR_M8
packet.dstAddr = b'\x00' * 15 + b'\x01'
packet.udp.dstPort = 1000
data = packet.to_bytes_packed()
test_ports['RV_test']['handle'].publish(data)
sleep(2)

print('\nsending test_data...')
packet = LoCD.new_message()
packet.dstMac = 0xff
packet.dstAddrType = LO_ADDR_M8
packet.dstAddr = b'\x00' * 15 + b'\x01'
packet.udp.dstPort = 2001
packet.data = "test_data...\n"
data = packet.to_bytes_packed()
test_ports['RV_test']['handle'].publish(data)

packet = LoCD.new_message()
packet.dstMac = 0xff
packet.dstAddrType = LO_ADDR_M8
packet.dstAddr = b'\x00' * 15 + b'\x01'
packet.udp.dstPort = 2000
packet.data = pc_mac.to_bytes(1, 'big') + (2000).to_bytes(2, 'big') + \
              (LO_ADDR_LL0).to_bytes(1, 'big') + b'\x00' * 16
data = packet.to_bytes_packed()
test_ports['RV_test']['handle'].publish(data)

print('done ...')
while True:
    sleep(1)

