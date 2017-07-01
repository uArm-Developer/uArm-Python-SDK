#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import _thread, threading
import serial


class SerialAscii(threading.Thread):
    def __init__(self, ufc, node, iomap, dev_port, baud):
        
        self.ports = {
            'in': {'dir': 'in', 'type': 'topic', 'callback': self.in_cb},
            'out': {'dir': 'out', 'type': 'topic'},
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb}
        }
        
        self.node = node
        ufc.node_init(node, self.ports, iomap)
        
        # TODO: maintain serial connection by service callback
        self.com = serial.Serial(port = dev_port, baudrate = baud)
        if not self.com.isOpen():
            raise Exception('serial open failed')
        threading.Thread.__init__(self)
        self.daemon = True
        self.alive = True
        self.start()
    
    def run(self):
        while self.alive:
            line = self.com.readline()
            if not line:
                continue
            if self.ports['out']['handle']:
                self.ports['out']['handle'].publish(line.decode().rstrip())
            #print('{}: -> '.format(self.node) + line.decode().rstrip())
        self.com.close()
    
    def stop(self):
        self.alive = False
        self.join()
    
    def in_cb(self, message):
        self.com.write(bytes(message + '\n', 'utf-8'))
        #print('{}: <- '.format(self.node) + message)
    
    def service_cb(self, message):
        pass


