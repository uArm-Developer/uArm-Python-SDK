#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import _thread, threading
import serial
from serial.tools import list_ports
from ..utils.select_serial_port import select_port
from ..utils.log import *

class SerialAscii(threading.Thread):
    def __init__(self, ufc, node, iomap, dev_port = None, baud = 115200, filters = None):
        
        self.ports = {
            'in': {'dir': 'in', 'type': 'topic', 'callback': self.in_cb},
            'out': {'dir': 'out', 'type': 'topic'},
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb}
        }
        
        self.node = node
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        ufc.node_init(node, self.ports, iomap)
        
        dev_port = select_port(logger = self.logger, dev_port = dev_port, filters = filters)
        if not dev_port:
            quit(1)
        
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
            line = ''.join(map(chr, line)).rstrip()
            self.logger.log(logging.VERBOSE, '-> ' + line)
            if self.ports['out']['handle']:
                self.ports['out']['handle'].publish(line)
        self.com.close()
    
    def stop(self):
        self.alive = False
        self.join()
    
    def in_cb(self, message):
        self.logger.log(logging.VERBOSE, '<- ' + message)
        self.com.write(bytes(map(ord, message + '\n')))
    
    def service_cb(self, message):
        pass


