#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from ..utils.module_group import ModuleGroup
from ..comm.cdbus2raw import Cdbus2Raw
from ..comm.protocol_ascii import ProtocolAscii
from .swift_body import SwiftBody
from .gripper import Gripper
from .pump import Pump
from .keys import Keys

class Swift(ModuleGroup):
    '''\
    The top module of swift and swift_pro (via CDBUS2RAW module)
    '''
    
    def __init__(self, ufc, node, iomap, **kwargs):
        
        self.sub_nodes = [
            {
                'module': Cdbus2Raw,
                'node': 'cdbus2raw',
                'args': ['dev_filter', 'listen_port'],
                'iomap': {
                    'service':      'outer: cdbus2raw',
                    
                    'raw_down2up':  'inner: pkt_ser2ptc',
                    'raw_up2down':  'inner: pkt_ptc2ser',
                    
                    'lo_service':   'outer: lo_service',
                    'RV_socket':    'outer: cdbus2raw_RV',
                    'RA_socket':    'outer: cdbus2raw_RA',
                    'SA_listen':    'outer: cdbus2raw_SA'
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
                'module': SwiftBody,
                'node': 'swift_body',
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
            },
            {
                'module': Keys,
                'node': 'keys',
                'iomap': {
                    'service':  'outer: keys',
                    'key0':     'outer: key0',
                    'key1':     'outer: key1',
                    'cmd_sync': 'outer: ptc_sync',
                    'report':   'outer: ptc_report'
                }
            }
        ]
        
        super().__init__(ufc, node, iomap, **kwargs)


