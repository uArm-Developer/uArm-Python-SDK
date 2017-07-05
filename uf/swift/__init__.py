#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from ..comm.serial_ascii import SerialAscii
from ..comm.protocol_ascii import ProtocolAscii
from .swift_body import SwiftBody
from .gripper import Gripper
from .pump import Pump
from .keys import Keys

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
        if 'pos_out' in iomap.keys():
            top_iomap['pos_out'] = iomap['pos_out']
        if 'buzzer' in iomap.keys():
            top_iomap['buzzer'] = iomap['buzzer']
        if 'service' in iomap.keys():
            top_iomap['service'] = iomap['service']
        if len(top_iomap):
            top_iomap['cmd_async'] = node + '/ptc_async'
            top_iomap['cmd_sync'] = node + '/ptc_sync'
            top_iomap['report'] = node + '/ptc_report'
            self.swift_body = SwiftBody(ufc, node + '/swift_body', top_iomap)
        
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
        
        keys_iomap = {}
        if 'keys' in iomap.keys():
            keys_iomap['service'] = iomap['keys']
        if 'key0' in iomap.keys():
            keys_iomap['key0'] = iomap['key0']
        if 'key1' in iomap.keys():
            keys_iomap['key1'] = iomap['key1']
        if len(keys_iomap):
            keys_iomap['cmd_sync'] = node + '/ptc_sync'
            keys_iomap['report'] = node + '/ptc_report'
            self.keys = Keys(ufc, node + '/keys', keys_iomap)

