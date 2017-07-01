#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from ..comm.serial_ascii import SerialAscii
from ..comm.protocol_ascii import ProtocolAscii
from .swift_top import SwiftTop

class Swift():
    def __init__(self, ufc, node, iomap, dev_port = '/dev/ttyACM0', baud = 115200):
        
        ser_iomap = {
            'out': node + '/pkt_ser2ptc',
            'in': node + '/pkt_ptc2ser'
        }
        ptc_iomap = {
            'cmd_async': node + '/ptc_async',
            'cmd_sync': node + '/ptc_sync',
            #'report': node + '/ptc_report',
            
            'packet_in': node + '/pkt_ser2ptc',
            'packet_out': node + '/pkt_ptc2ser'
            
        }
        top_iomap = {
            'pos_in': iomap['pos_in'], # TODO: avoid KeyError if not specified
            'service': iomap['service'],
            
            'cmd_async': node + '/ptc_async',
            'cmd_sync': node + '/ptc_sync'
        }
        
        self.ser_ascii = SerialAscii(ufc, node + '/ser_ascii', ser_iomap, dev_port, baud)
        self.ptc_ascii = ProtocolAscii(ufc, node + '/ptc_ascii', ptc_iomap)
        self.swift_top = SwiftTop(ufc, node + '/swift_top', top_iomap)


