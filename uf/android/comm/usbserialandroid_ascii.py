#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Author: Adrian Clark <adrian.clark@canterbury.ac.nz>
# Modifed from file written by: Duke Fong <duke@ufactory.cc>


import _thread, threading

# Import USB 4 Android and USB Serial 4 Android libraries
from usb4a import usb
from usbserial4a import serial4a

# We need to use the select_port function defined in these scripts as the port selection is slightly different
from ..utils.usbserialandroid_select_serial_port import select_port
from ...utils.log import *

class USBSerialAndroidAscii(threading.Thread):
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
        
        # Use the USB Serial 4 Android Serial Port Function to open 
        self.com =  serial4a.get_serial_port(dev_port.name, baud, 8, 'N', 1)

        if not self.com.isOpen():
            raise Exception('serial open failed')
        threading.Thread.__init__(self)
        self.daemon = True
        self.alive = True
        self.start()
    
    def run(self):
        while self.alive:
            # Read_Until is the equivalent function to ReadLines
            line = self.com.read_until()
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


