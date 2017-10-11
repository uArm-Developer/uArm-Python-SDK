#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from .swift_api import SwiftAPI
from ..swift.grove.ultrasonic import Ultrasonic
from ..utils.log import *


class SwiftWithUltrasonic(SwiftAPI):
    '''
    The API wrapper of swift and swift_pro
    default kwargs: dev_port = None, baud = 115200, filters = {'hwid': 'USB VID:PID=2341:0042'}
                    ultrasonic_port = 'D8'
    '''
    def __init__(self, **kwargs):
        '''
        '''
        
        super().__init__(**kwargs)
        
        # init ultrasonic node:
        
        ultrasonic_iomap = {
            'service':      'ultrasonic',
            'distance':     'ultrasonic_report',
            'cmd_sync':     'ptc_sync',
            'report':   'ptc_report'
        }
        
        if 'ultrasonic_port' not in kwargs:
            kwargs['ultrasonic_port'] = 'D8'
        self._nodes['ultrasonic'] = Ultrasonic(self._ufc, 'ultrasonic', ultrasonic_iomap, port = kwargs['ultrasonic_port'])
        
        # init ultrasonic_api node:
        
        self._ultrasonic_ports = {
            'ultrasonic':        {'dir': 'out', 'type': 'service'},
            'ultrasonic_report': {'dir': 'in', 'type': 'topic', 'callback': self._ultrasonic_cb}
        }
        
        self._ultrasonic_iomap = {
            'ultrasonic':        'ultrasonic',
            'ultrasonic_report': 'ultrasonic_report'
        }
        
        self.ultrasonic_cb = None
        
        self._ultrasonic_node = 'ultrasonic_api'
        self._ultrasonic_logger = logging.getLogger(self._ultrasonic_node)
        self._ufc.node_init(self._ultrasonic_node, self._ultrasonic_ports, self._ultrasonic_iomap)
    
    
    def _ultrasonic_cb(self, msg):
        if self.ultrasonic_cb != None:
            self.ultrasonic_cb(int(msg))
    
    def set_report_ultrasonic(self, interval):
        '''
        Report distance from ultrasonic in (interval) microsecond.
        
        Args:
            interval: seconds, if 0 disable report
        
        Returns:
            None
        '''
        cmd = 'set report_distance on {}'.format(round(interval, 2))
        ret = self._ultrasonic_ports['ultrasonic']['handle'].call(cmd)
        if ret.startswith('ok'):
            return
        self._logger.error('set_report_ultrasonic ret: %s' % ret)
    
    def register_ultrasonic_callback(self, callback = None):
        '''
        Set function to receiving current distance from ultrasonic sensor.
        Unit: cm
        
        Args:
            callback: set the callback function, undo by setting to None
        
        Returns:
            None
        '''
        self.ultrasonic_cb = callback
    
    def get_ultrasonic(self):
        '''
        Get current distance from ultrasonic sensor
        
        Returns:
            int value of distance, unit: cm
        '''
        ret = self._ultrasonic_ports['ultrasonic']['handle'].call('get value')
        
        if ret.startswith('ok, '):
            return int(ret[4:])
        self._ultrasonic_logger.error('get value ret: %s' % ret)
        return None

