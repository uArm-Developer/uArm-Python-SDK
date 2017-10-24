#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>
#

from .locd_serdes import LoCD
from ...utils.log import *


class Dispatcher():
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            # iomap.keys():     # first field: (A: down2up; V: up2down)
            #   RV_test         #   RV:     UDP request
            #   RA_test         #   RA:     UDP answer
            #   SA1000_dev_info #   SA+num: UDP service request
            #   IA135_ns        #   IA+num: ICMP down2up
            #   IA136_na        #   IA+num: ICMP down2up
            
            'lo_up2down_repl_src':  {'dir': 'out', 'type': 'topic'},
            'lo_down2up': {'dir': 'in', 'type': 'topic',
                    'callback': self.lo_down2up, 'data_type': bytes}
        }
        
        class Ephemeral():
            def __init__(self, owner, begin, end, name):
                self.owner = owner
                self.begin = begin
                self.end = end
                self.cur = begin
                self.has_answer = False
                self.name = name # with out first field
            
            def repl_srcport_cb(self, msg):
                packet = LoCD.from_bytes_packed(msg).as_builder()
                packet.udp.srcPort = self.cur
                data = packet.to_bytes_packed()
                self.owner.ports['lo_up2down_repl_src']['handle'].publish(data)
                self.cur += 1
                if self.cur == self.end:
                    self.cur = self.begin
        
        self.ephemerals = []
        
        self.services = {
            #1000: 'SA1000_dev_info'
        }
        
        self.icmps = {
            #136: 'IA136_na'
        }
        
        port_start = 0xf000
        
        # append ports:
        for k, path in iomap.items():
            if k in self.ports.keys():
                continue
            ff = k.split('_', 1)[0]
            if ff[:2] == 'IA':
                self.ports[k] = {'dir': 'out', 'type': 'topic'}
                self.icmps[int(ff[2:])] = k
            elif ff[:2] == 'SA':
                self.ports[k] = {'dir': 'out', 'type': 'topic'}
                self.services[int(ff[2:])] = k
            elif ff[:2] == 'RV':
                eph = Ephemeral(self, port_start, port_start + 10, k[3:])
                port_start += 10
                self.ephemerals.append(eph)
                self.ports[k] = {'dir': 'in', 'type': 'topic',
                                 'callback': eph.repl_srcport_cb, 'data_type': bytes}
            elif ff[:2] == 'RA':
                self.ports[k] = {'dir': 'out', 'type': 'topic'}
                for eph in self.ephemerals:
                    if eph.name == k[3:]:
                        eph.has_answer = True
        
        self.node = node
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        ufc.node_init(node, self.ports, iomap)
    
    def lo_down2up(self, msg):
        packet = LoCD.from_bytes_packed(msg)
        if packet.which() == 'udp':
            if packet.udp.dstPort >= 0xf000:
                for eph in self.ephemerals:
                    if eph.begin <= packet.udp.dstPort < eph.end:
                        if eph.has_answer:
                            self.ports['RA_' + eph.name]['handle'].publish(msg)
                        break
            elif packet.udp.dstPort in self.services.keys():
                name = self.services[packet.udp.dstPort]
                self.ports[name]['handle'].publish(msg)
        elif packet.icmp.type in self.icmps.keys():
            name = self.icmps[packet.icmp.type]
            self.ports[name]['handle'].publish(msg)


