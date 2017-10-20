#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from ..utils.log import *


class Keys():
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            'key0': {'dir': 'out', 'type': 'topic'},
            'key1': {'dir': 'out', 'type': 'topic'},
            
            'cmd_sync': {'dir': 'out', 'type': 'service'},
            'report': {'dir': 'in', 'type': 'topic', 'callback': self.report_cb}
        }
        
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        ufc.node_init(node, self.ports, iomap)
    
    def report_cb(self, msg):
        if self.ports['key0']['handle']:
            if msg == '4 B0 V1':
                self.ports['key0']['handle'].publish('short press')
            elif msg == '4 B0 V2':
                self.ports['key0']['handle'].publish('long press')
        if self.ports['key1']['handle']:
            if msg == '4 B1 V1':
                self.ports['key1']['handle'].publish('short press')
            elif msg == '4 B1 V2':
                self.ports['key1']['handle'].publish('long press')
    
    def service_cb(self, msg):
        msg = msg.split(' ', 2)
        
        if msg[1] == 'key_owner':
            if msg[0] == 'get':
                return 'err, get not support'
            
            if msg[0] == 'set':
                self.logger.debug('set value: %s' % msg[2])
                if msg[2] == 'default':
                    return self.ports['cmd_sync']['handle'].call('P2213 V1')
                elif msg[2] == 'user':
                    return self.ports['cmd_sync']['handle'].call('P2213 V0')
                return 'err, value not support'

