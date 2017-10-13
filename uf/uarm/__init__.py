#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from ..utils.module_group import ModuleGroup
from ..comm.serial_ascii import SerialAscii
from ..comm.protocol_ascii import ProtocolAscii
from .uarm_body import UarmBody
from .gripper import Gripper
from .pump import Pump

class Uarm(ModuleGroup):
    '''\
    The top module of uArm Metal
    default kwargs: dev_port = None, baud = 115200, filters = {'hwid': 'USB VID:PID=0403:6001'}
    '''
    
    def __init__(self, ufc, node, iomap, **kwargs):
    
        self.sub_nodes = [
            {
                'module': SerialAscii,
                'node': 'serial_ascii',
                'args': ['dev_port', 'baud', 'filters'],
                'iomap': {
                    'out': 'inner: pkt_ser2ptc',
                    'in':  'inner: pkt_ptc2ser'
                }
            },
            {
                'module': ProtocolAscii,
                'node': 'ptc_ascii',
                'args': ['cmd_pend_size'],
                'iomap': {
                    'cmd_async':  'outer: ptc_async',
                    'cmd_sync':   'outer: ptc_sync',
                    'report':     'outer: ptc_report',
                    'service':    'outer: ptc',
                    
                    'packet_in':  'inner: pkt_ser2ptc',
                    'packet_out': 'inner: pkt_ptc2ser'
                }
            },
            {
                'module': UarmBody,
                'node': 'uarm_body',
                'iomap': {
                    'pos_in':    'outer: pos_in',
                    'pos_out':   'outer: pos_out',
                    'buzzer':    'outer: buzzer',
                    'service':   'outer: service',
                    
                    'cmd_async': 'outer: ptc_async',
                    'cmd_sync':  'outer: ptc_sync',
                    'report':    'outer: ptc_report'
                }
            },
            {
                'module': Gripper,
                'node': 'gripper',
                'iomap': {
                    'service':  'outer: gripper',
                    'cmd_sync': 'outer: ptc_sync'
                }
            },
            {
                'module': Pump,
                'node': 'pump',
                'iomap': {
                    'service':      'outer: pump',
                    'limit_switch': 'outer: limit_switch',
                    'cmd_sync':     'outer: ptc_sync',
                    'report':       'outer: ptc_report'
                }
            }
        ]
        
        if 'dev_port' not in kwargs:
            kwargs['dev_port'] = None
        if 'baud' not in kwargs:
            kwargs['baud'] = 115200
        if 'filters' not in kwargs:
            kwargs['filters'] = {'hwid': 'USB VID:PID=0403:6001'}
        if 'cmd_pend_size' not in kwargs:
            kwargs['cmd_pend_size'] = 2
        super().__init__(ufc, node, iomap, **kwargs)


