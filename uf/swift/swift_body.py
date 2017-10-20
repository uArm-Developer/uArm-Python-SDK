#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from ..utils.log import *

csys_gstr = {
    'polar': 'G2201 ',
    'cartesian': 'G0 '
}

class SwiftBody():
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
        
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        self.mode = 'play'
        self.coordinate_system = 'cartesian'
        
        ufc.node_init(node, self.ports, iomap)
    
    def buzzer_cb(self, msg):
        '''msg format: "F1000 T200", F: frequency, T: time period'''
        self.ports['cmd_async']['handle'].publish('M2210 ' + msg)
    
    # TODO: create a thread to maintain device status and read dev_info
    def read_dev_info(self):
        info = []
        for c in range(2201, 2206):
            ret = ''
            while not ret.startswith('ok'):
                ret = self.ports['cmd_sync']['handle'].call('P%d' % c)
            info.append(ret.split(' ', 1)[1])
        return ' '.join(info)
    
    def report_cb(self, msg):
        if msg == '5 V1': # power on
            pass
        if msg[:2] == '3 ' and self.ports['pos_out']['handle']:
            self.ports['pos_out']['handle'].publish(msg[2:])
    
    def pos_in_cb(self, msg):
        if self.ports['cmd_async']['handle']:
            if not msg.startswith('_T'):
                cmd = '_T10 ' # timeout 10s
            else:
                tmp = msg.split(' ', 1)
                cmd = tmp[0] + ' '
                msg = tmp[1]
            cmd += csys_gstr[self.coordinate_system] + msg
            self.ports['cmd_async']['handle'].publish(cmd)
    
    def service_cb(self, msg):
        msg = msg.split(' ', 2)
        
        if msg[1] == 'mode':
            if msg[0] == 'get':
                return 'ok, ' + self.mode
        
        if msg[1] == 'dev_info':
            if msg[0] == 'get':
                return 'ok, ' + self.read_dev_info()
        
        if msg[1] == 'coordinate_system':
            if msg[0] == 'get':
                return 'ok, ' + self.coordinate_system
            if msg[0] == 'set':
                self.logger.debug('coordinate_system: %s -> %s' % (self.coordinate_system, msg[2]))
                self.coordinate_system = msg[2]
                return 'ok'
        
        if msg[1] == 'report_pos':
            if msg[0] == 'set':
                if msg[2] == 'off':
                    return self.ports['cmd_sync']['handle'].call('M2120 V0')
                elif msg[2].startswith('on '):
                    # format e.g.: set report_pos on 0.2
                    return self.ports['cmd_sync']['handle'].call('M2120 V' + msg[2][3:])
        
        if msg[1] == 'cmd_sync':
            if msg[0] == 'set':
                return self.ports['cmd_sync']['handle'].call(msg[2])
        
        if msg[1] == 'cmd_async':
            if msg[0] == 'set':
                self.ports['cmd_async']['handle'].publish(msg[2])
                return 'ok'


