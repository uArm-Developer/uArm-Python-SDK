#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from ...utils.log import *


class Ultrasonic():
    def __init__(self, ufc, node, iomap, port = 'D8'):
        
        self.ports = {
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            'distance': {'dir': 'out', 'type': 'topic'},
            
            'cmd_sync': {'dir': 'out', 'type': 'service'},
            'report': {'dir': 'in', 'type': 'topic', 'callback': self.report_cb}
        }
        
        self.distance = '-1'
        self.port = port
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        ufc.node_init(node, self.ports, iomap)
    
    def report_cb(self, msg):
        if msg.startswith('10 N12 V'):
            self.distance = msg[8:]
            if self.ports['distance']['handle']:
                self.ports['distance']['handle'].publish(self.distance)
    
    def service_cb(self, msg):
        msg = msg.split(' ', 2)
        
        if msg[1] == 'value':
            if msg[0] == 'get':
                return 'ok, ' + self.distance
            else:
                return 'err, action "{}" not allowed for value'.format(action)
        
        if msg[1] == 'report_distance':
            if msg[0] == 'set':
                if msg[2] == 'off':
                    return self.ports['cmd_sync']['handle'].call('M2301 N12 V0')
                elif msg[2].startswith('on '):
                    # init, choose port D8 or D9, the buggy firmware always return ok even set to a wrong port number
                    self.ports['cmd_sync']['handle'].call('M2300 N12 ' + self.port)
                    # unit: microsecond, format e.g.: set report_distance on 500
                    return self.ports['cmd_sync']['handle'].call('M2301 N12 V' + msg[2][3:])

