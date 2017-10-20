#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from time import sleep
from ..utils.log import *


class Gripper():
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            
            'cmd_sync': {'dir': 'out', 'type': 'service'},
        }
        
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        ufc.node_init(node, self.ports, iomap)
    
    def set_gripper(self, val):
        if val == 'on':
            self.ports['cmd_sync']['handle'].call('M232 V1')
        else:
            self.ports['cmd_sync']['handle'].call('M232 V0')
        
        # TODO: modify the default timeout time with a service command
        for _ in range(20):
            ret = self.ports['cmd_sync']['handle'].call('P232')
            if val == 'on':
                if ret == 'OK V2': # grabbed
                    return 'ok'
            else:
                if ret == 'OK V0': # stop
                    return 'ok'
            sleep(0.5)
        return 'err, timeout for {}, last ret: {}'.format(val, ret)
    
    def service_cb(self, msg):
        msg = msg.split(' ', 2)
        
        if msg[1] == 'value':
            if msg[0] == 'get':
                ret = self.ports['cmd_sync']['handle'].call('P232')
                self.logger.debug('get value ret: %s' % ret)
                
                if ret == 'OK V0':
                    return 'ok, stoped'
                elif ret == 'OK V1':
                    return 'ok, working'
                elif ret == 'OK V2':
                    return 'ok, grabbed'
                else:
                    return 'err, unkown ret: %s' % ret
            
            if msg[0] == 'set':
                self.logger.debug('set value: %s' % msg[2])
                return self.set_gripper(msg[2])


