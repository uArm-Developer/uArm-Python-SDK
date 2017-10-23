#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import _thread, threading
from queue import Queue
from time import sleep
from ..utils.log import *


class ProtocolAscii():
    def __init__(self, ufc, node, iomap, cmd_pend_size = 2, timeout = 1):
        
        self.ports = {
            'cmd_async': {'dir': 'in', 'type': 'topic', 'callback': self.cmd_async_cb},
            'cmd_sync': {'dir': 'in', 'type': 'service', 'callback': self.cmd_sync_cb},
            
            'report': {'dir': 'out', 'type': 'topic'},
            'status': {'dir': 'out', 'type': 'topic'}, # report lost, etc...
            
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            
            'packet_in': {'dir': 'in', 'type': 'topic', 'callback': self.packet_in_cb},
            'packet_out': {'dir': 'out', 'type': 'topic'},
        }
        
        self.node = node
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        self.cmd_pend = {}
        self.cmd_pend_size = cmd_pend_size
        self.cmd_pend_c = threading.Condition()
        self.timeout = timeout
        self.cnt_lock = _thread.allocate_lock()
        self.cnt = 1 # no reply if cnt == 0, FIXME
        ufc.node_init(node, self.ports, iomap)
    
    
    class Cmd():
        def __init__(self, owner, cnt, msg, timeout):
            self.owner = owner
            self.cnt = cnt
            self.msg = msg
            self.ret = Queue(1)
            self.timer = threading.Timer(timeout, self.timeout_cb)
            self.timer.start()
        
        def delete(self):
            del self.owner.cmd_pend[self.cnt]
            with self.owner.cmd_pend_c:
                self.owner.cmd_pend_c.notifyAll()
        
        def finish(self, msg):
            self.timer.cancel()
            self.delete()
            self.ret.put(msg)
        
        def get_ret(self):
            return self.ret.get()
        
        def timeout_cb(self):
            self.delete() # TODO: avoid KeyError if the 'finish' called at same time
            self.owner.logger.warning('cmd "#{} {}" timeout'.format(self.cnt, self.msg))
            self.ret.put('err, timeout')
    
    
    def packet_in_cb(self, msg):
        #print('{}: <- '.format(self.node) + msg)
        if len(msg) < 2:
            return
        if msg[0:1] == '@':
            if self.ports['report']['handle']:
                self.logger.log(logging.VERBOSE, 'report: ' + msg)
                self.ports['report']['handle'].publish(msg[1:])
        elif msg[0:1] == '$':
            index = msg.find(' ')
            index = index if index != -1 else len(msg)
            cnt = int(msg[1:index])
            if cnt in self.cmd_pend.keys():
                # TODO: avoid KeyError
                self.cmd_pend[cnt].finish(msg[index + 1:])
            else:
                pass # warning...
    
    def cmd_async_cb(self, msg):
        with self.cnt_lock:
            with self.cmd_pend_c:
                while len(self.cmd_pend) >= self.cmd_pend_size:
                    self.cmd_pend_c.wait()
            if msg.startswith('_T'):
                tmps = msg[2:].split(' ', 1)
                timeout = int(tmps[0])
                msg = tmps[1]
            else:
                timeout = self.timeout
            cmd = self.Cmd(self, self.cnt, msg, timeout)
            self.cmd_pend[self.cnt] = cmd
            self.ports['packet_out']['handle'].publish('#{} '.format(self.cnt) + msg)
            self.cnt += 1
            if self.cnt == 10000:
                self.cnt = 1
        return cmd
    
    def cmd_sync_cb(self, msg):
        cmd = self.cmd_async_cb(msg)
        return cmd.get_ret()
    
    def service_cb(self, msg):
        msg = msg.split(' ', 2)
        
        if msg[1] == 'flush':
            if msg[0] == 'set':
                sleep(0.1)
                with self.cmd_pend_c:
                    while len(self.cmd_pend) != 0 or self.cnt_lock.locked():
                        self.cmd_pend_c.wait()
                return 'ok'
        
        if msg[1] == 'pend':
            if msg[0] == 'get':
                return 'ok, pend: %d' % len(self.cmd_pend)


