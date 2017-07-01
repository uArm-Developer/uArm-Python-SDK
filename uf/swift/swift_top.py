#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import _thread, threading
from queue import Queue

csys_gstr = {
    'polar': 'G2201 ',
    'cartesian': 'G0 '
}

class SwiftTop():
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            'pos_in': {'dir': 'in', 'type': 'topic', 'callback': self.pos_in_cb},
            'pos_out': {'dir': 'out', 'type': 'topic'}, # report current position
            
            #'status': {'dir': 'out', 'type': 'topic'}, # report unconnect, etc...
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            
            'cmd_async': {'dir': 'out', 'type': 'topic'},
            'cmd_sync': {'dir': 'out', 'type': 'service'},
        }
        
        self.mode = 'play'
        self.coordinate_system = 'cartesian'
        
        ufc.node_init(node, self.ports, iomap)
        
    
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
                return self.mode
                
        if param == 'coordinate_system':
            if action == 'get':
                return self.coordinate_system
            if action == 'set':
                print('coordinate_system: %s -> %s' % (self.coordinate_system, words[1]))
                self.coordinate_system = words[1]
                return 'ok'
                
        if param == 'command':
            if action == 'set':
                return self.ports['cmd_sync']['handle'].call(words[1])


