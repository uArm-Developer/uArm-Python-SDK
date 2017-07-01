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
from .gripper import Gripper
from .pump import Pump

class Swift():
    '''The top module of swift/swift_pro'''
    def __init__(self, ufc, node, iomap, dev_port = '/dev/ttyACM0', baud = 115200):
        
        ser_iomap = {
            'out': node + '/pkt_ser2ptc',
            'in': node + '/pkt_ptc2ser'
        }
        ptc_iomap = {
            'cmd_async': node + '/ptc_async',
            'cmd_sync': node + '/ptc_sync',
            'report': node + '/ptc_report',
            
            'packet_in': node + '/pkt_ser2ptc',
            'packet_out': node + '/pkt_ptc2ser'
        }
        self.ser_ascii = SerialAscii(ufc, node + '/ser_ascii', ser_iomap, dev_port, baud)
        self.ptc_ascii = ProtocolAscii(ufc, node + '/ptc_ascii', ptc_iomap)
        
        top_iomap = {}
        if 'pos_in' in iomap.keys():
            top_iomap['pos_in'] = iomap['pos_in']
        if 'service' in iomap.keys():
            top_iomap['service'] = iomap['service']
        if len(top_iomap):
            top_iomap['cmd_async'] = node + '/ptc_async'
            top_iomap['cmd_sync'] = node + '/ptc_sync'
            top_iomap['report'] = node + '/ptc_report'
            self.swift_top = SwiftTop(ufc, node + '/swift_top', top_iomap)
        
        if 'gripper' in iomap.keys():
            gripper_iomap = {
                'service': iomap['gripper'],
                
                'cmd_sync': node + '/ptc_sync'
            }
            self.gripper = Gripper(ufc, node + '/gripper', gripper_iomap)
        
        pump_iomap = {}
        if 'pump' in iomap.keys():
            pump_iomap['service'] = iomap['pump']
        if 'limit_switch' in iomap.keys():
            pump_iomap['limit_switch'] = iomap['limit_switch']
        if len(pump_iomap):
            pump_iomap['cmd_sync'] = node + '/ptc_sync'
            pump_iomap['report'] = node + '/ptc_report'
            self.pump = Pump(ufc, node + '/pump', pump_iomap)

