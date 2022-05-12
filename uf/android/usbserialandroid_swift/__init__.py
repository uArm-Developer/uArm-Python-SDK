#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Author: Adrian Clark <adrian.clark@canterbury.ac.nz>
# Modifed from file written by: Duke Fong <duke@ufactory.cc>

from ...utils.module_group import ModuleGroup
from ..comm.usbserialandroid_ascii import USBSerialAndroidAscii
from ...comm.protocol_ascii import ProtocolAscii

# I had to duplicate these files otherwise it pulls in original the
# original Swift files, and then crashes requiring PySerial, which
# we don't actually need
from .swift_body import SwiftBody
from .gripper import Gripper
from .pump import Pump
from .keys import Keys

# A new class was used so we can use the USBSerialAndroidAscii Module
# Rather than the one based on PySerial
class UsbSerialAndroid_Swift(ModuleGroup):
    '''\
    The top module of swift and swift_pro
    default kwargs: dev_port = None, baud = 115200, filters = {'hwid': 'USB VID:PID=2341:0042'}
    '''
    
    def __init__(self, ufc, node, iomap, **kwargs):
        
        self.sub_nodes = [
            {
                # Module here is changed
                'module': USBSerialAndroidAscii,
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
        
        if 'dev_port' not in kwargs:
            kwargs['dev_port'] = None
        if 'baud' not in kwargs:
            kwargs['baud'] = 115200
        if 'filters' not in kwargs:
            kwargs['filters'] = {'hwid': 'USB VID:PID=2341:0042'}
        if 'cmd_pend_size' not in kwargs:
            kwargs['cmd_pend_size'] = 2
        super().__init__(ufc, node, iomap, **kwargs)


