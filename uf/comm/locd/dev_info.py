#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

import queue
import capnp
from socket import gethostname

import locd_capnp
from .locd import *
from ...utils.log import *

class DevInfo():
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            'lo_up2down_repl_src': {'dir': 'out', 'type': 'topic'},
            'lo_down2up': {'dir': 'in', 'type': 'topic',
                    'callback': self.lo_down2up, 'data_type': bytes}
        }
        
        self.logger = logging.getLogger(node)
        ufc.node_init(node, self.ports, iomap)
    
    def lo_down2up(self, msg):
        packet = locd_capnp.LoCD.from_bytes_packed(msg)
        if packet.which() != 'udp' or packet.udp.dstPort != 1000:
            return
        packet.data = 'pyuf, ser ' + gethostname()
        self.logger.debug('answer: pyuf, ser ' + gethostname())
        data = packet.to_bytes_packed()
        self.ports['lo_up2down_repl_src']['handle'].publish(data)


