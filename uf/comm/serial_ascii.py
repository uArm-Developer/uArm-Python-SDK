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
from ..utils.log import *

class SerialAscii(threading.Thread):
    def __init__(self, ufc, node, iomap, dev_port = None, baud = 115200, filters = None):
        
        self.ports = {
            'in': {'dir': 'in', 'type': 'topic', 'callback': self.in_cb},
            'out': {'dir': 'out', 'type': 'topic'},
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb}
        }
        
        self.node = node
        self.logger = logging.getLogger(node)
        ufc.node_init(node, self.ports, iomap)
        
        if filters != None and dev_port == None:
            list_all = False
            for d in list_ports.comports():
                is_match = True
                for k, v in filters.items():
                    if not hasattr(d, k):
                        continue
                    a = getattr(d, k)
                    if not a:
                        a = ''
                    if not a.startswith(v):
                        is_match = False
                if is_match:
                    if dev_port == None:
                        dev_port = d.device
                        self.logger.info('choose device: ' + dev_port)
                        self._dump_port(d)
                    else:
                        self.logger.warning('find more than one port')
                        list_all = True
            if list_all:
                self.logger.info('current filter: {}, all ports:'.format(filters))
                self._dump_ports()
        
        if not dev_port:
            if filters:
                self.logger.error('port not found, current filter: {}, all ports:'.format(filters))
            else:
                self.logger.error('please specify dev_port or filters, all ports:')
            self._dump_ports()
            quit(1)
        
        # TODO: maintain serial connection by service callback
        self.com = serial.Serial(port = dev_port, baudrate = baud)
        if not self.com.isOpen():
            raise Exception('serial open failed')
        threading.Thread.__init__(self)
        self.daemon = True
        self.alive = True
        self.start()
    
    def _dump_port(self, d):
        self.logger.info('{}:'.format(d.device))
        self.logger.info('  hwid        : "{}"'.format(d.hwid))
        self.logger.info('  manufacturer: "{}"'.format(d.manufacturer))
        self.logger.info('  product     : "{}"'.format(d.product))
        self.logger.info('  description : "{}"'.format(d.description))
    
    def _dump_ports(self):
        for d in list_ports.comports():
            self._dump_port(d)
    
    def run(self):
        while self.alive:
            line = self.com.readline()
            if not line:
                continue
            line = ''.join(map(chr, line)).rstrip()
            if self.ports['out']['handle']:
                self.ports['out']['handle'].publish(line)
            self.logger.log(logging.VERBOSE, '-> ' + line)
        self.com.close()
    
    def stop(self):
        self.alive = False
        self.join()
    
    def in_cb(self, message):
        self.com.write(bytes(map(ord, message + '\n')))
        self.logger.log(logging.VERBOSE, '<- ' + message)
    
    def service_cb(self, message):
        pass


