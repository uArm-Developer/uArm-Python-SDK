#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import _thread, threading
from queue import Queue
from ..utils.log import *

csys_gstr = {
    'polar': 'G201 ',
    'cartesian': 'G0 '
}

class UarmBody():
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            'pos_in': {'dir': 'in', 'type': 'topic', 'callback': self.pos_in_cb},
            'pos_out': {'dir': 'out', 'type': 'topic'}, # report current position
            
            'buzzer': {'dir': 'in', 'type': 'topic', 'callback': self.buzzer_cb},
            
            #'status': {'dir': 'out', 'type': 'topic'}, # report unconnect, etc...
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            
            'cmd_async': {'dir': 'out', 'type': 'topic'},
            'cmd_sync': {'dir': 'out', 'type': 'service'},
            'report': {'dir': 'in', 'type': 'topic', 'callback': self.report_cb}
        }
        
        self.logger = logging.getLogger(node)
        self.mode = 'play'
        self.coordinate_system = 'cartesian'
        
        ufc.node_init(node, self.ports, iomap)
    
    def buzzer_cb(self, msg):
        '''msg format: "F1000 T0.2", F: frequency, T: time period (s)'''
        self.ports['cmd_async']['handle'].publish('M210 ' + msg)
    
    # TODO: create a thread to maintain device status and read dev_info
    def read_dev_info(self):
        info = []
        for c in range(201, 206):
            ret = ''
            while not ret.startswith('OK'):
                ret = self.ports['cmd_sync']['handle'].call('P%d' % c)
            info.append(ret.split(' ', 1)[1])
        return ' '.join(info)
    
    def report_cb(self, msg):
        if msg[:2] == '3 ' and self.ports['pos_out']['handle']:
            self.ports['pos_out']['handle'].publish(msg[2:])
    
    def pos_in_cb(self, msg):
        if self.ports['cmd_async']['handle']:
            cmd = csys_gstr[self.coordinate_system] + msg
            self.ports['cmd_async']['handle'].publish(cmd)
    
    def service_cb(self, msg):
        words = msg.split(' ', 1)
        action = words[0]
        
        words = words[1].split(' ', 1)
        param = words[0]
        
        if param == 'mode':
            if action == 'get':
                return 'ok, ' + self.mode
        
        if param == 'dev_info':
            if action == 'get':
                return 'ok, ' + self.read_dev_info()
        
        if param == 'coordinate_system':
            if action == 'get':
                return 'ok, ' + self.coordinate_system
            if action == 'set':
                self.logger.debug('coordinate_system: %s -> %s' % (self.coordinate_system, words[1]))
                self.coordinate_system = words[1]
                return 'ok'
        
        if param == 'report_pos':
            if action == 'set':
                if words[1] == 'off':
                    return self.ports['cmd_sync']['handle'].call('M120 V0')
                elif words[1].startswith('on '):
                    # unit: second, format e.g.: set report_pos on 0.2
                    return self.ports['cmd_sync']['handle'].call('M120 V' + words[1][3:])
        
        if param == 'cmd_sync':
            if action == 'set':
                return self.ports['cmd_sync']['handle'].call(words[1])
        
        if param == 'cmd_async':
            if action == 'set':
                self.ports['cmd_async']['handle'].publish(words[1])
                return 'ok'


