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
from .locd.cdbus_serial import CdbusSerial
from .locd.uart2cdbus import Uart2Cdbus
from .locd.dispatcher import Dispatcher
from .locd.lond import LoND
from .locd.dev_info import DevInfo


class LocdViaUart2Cdbus(ModuleGroup):
    '''\
    The module group used for LoCD via UART2CDBUS
    default kwargs: dev_port = None, baud = 115200,
    filters = {'hwid': 'USB VID:PID=10C4:EA60'} #CP2102
    '''
    
    def __init__(self, ufc, node, iomap, **kwargs):
    
        self.sub_nodes = [
            {
                'module': CdbusSerial,
                'node': 'cdbus_serial',
                'args': ['dev_port', 'baud', 'filters'],
                'iomap': {
                    'up2down':              'inner: cd_up2down',
                    'down2up':              'inner: cd_down2up'
                }
            },
            {
                'module': Uart2Cdbus,
                'node': 'uart2cdbus',
                'iomap': {
                    'service':              'outer: lo_service',
                    
                    'lo_up2down':           'outer: lo_up2down',
                    'lo_up2down_repl_src':  'outer: lo_up2down_repl_src',
                    'lo_up2down_xchg':      'outer: lo_up2down_xchg',
                    'lo_down2up':           'outer: lo_down2up',
                    
                    'cd_up2down':           'inner: cd_up2down',
                    'cd_down2up':           'inner: cd_down2up'
                }
            },
            { # index: 2
                'module': Dispatcher,
                'node': 'dispatcher',
                'iomap': {
                    'SA1000_dev_info':      'inner: SA1000_dev_info',
                    'IA135_ns':             'inner: IA135_ns',
                    'IA136_na':             'inner: IA136_na',
                    
                    'lo_up2down_repl_src':  'outer: lo_up2down_repl_src',
                    'lo_down2up':           'outer: lo_down2up'
                }
            },
            {
                'module': LoND,
                'node': 'lond',
                'iomap': {
                    'lo_service':           'outer: lo_service',
                    
                    'lo_up2down':           'outer: lo_up2down',
                    'IA135_ns':             'inner: IA135_ns',
                    'IA136_na':             'inner: IA136_na'
                }
            },
            {
                'module': DevInfo,
                'node': 'dev_info',
                'iomap': {
                    'lo_up2down_xchg':      'outer: lo_up2down_xchg',
                    'SA1000_dev_info':      'inner: SA1000_dev_info'
                }
            }
        ]
        
        for k, path in iomap.items():
            if k[:2] == 'RV' or k[:2] == 'RA' or k[:2] == 'SA' or k[:2] == 'IA':
                self.sub_nodes[2]['iomap'][k] = 'outer: ' + k
        
        if 'dev_port' not in kwargs:
            kwargs['dev_port'] = None
        if 'baud' not in kwargs:
            kwargs['baud'] = 115200
        if 'filters' not in kwargs:
            kwargs['filters'] = {'hwid': 'USB VID:PID=10C4:EA60'}
        super().__init__(ufc, node, iomap, **kwargs)


