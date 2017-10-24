#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>
#
# Each node on the bus must answer dev_info request, which at UDP port 1000

import queue
from socket import gethostname

from .locd_serdes import LoCD
from .locd import *
from ...utils.log import *

class DevInfo():
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            'lo_up2down_xchg': {'dir': 'out', 'type': 'topic'},
            'SA1000_dev_info': {'dir': 'in', 'type': 'topic',
                    'callback': self.lo_down2up, 'data_type': bytes}
        }
        
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        ufc.node_init(node, self.ports, iomap)
    
    def lo_down2up(self, msg):
        packet = LoCD.from_bytes_packed(msg)
        in_data = packet.data
        packet.data = ('M: pyuf; S: ' + gethostname()).encode('ascii') # replace data content
        
        if len(in_data) != 0 and packet.data.find(in_data) == -1:
            self.logger.debug('filtered by: ', in_data)
            return
        
        self.logger.debug('answer: pyuf, ser ' + gethostname())
        data = packet.to_bytes_packed()
        self.ports['lo_up2down_xchg']['handle'].publish(data)


