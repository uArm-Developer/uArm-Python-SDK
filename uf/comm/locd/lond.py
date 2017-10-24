#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>
#
# Neighbor Discovery for IP version 6 (IPv6)
# Adapt for 6LoCD

import threading
from time import sleep
from random import randint

from .locd_serdes import LoCD
from .locd import *
from ...utils.log import *

ND_TYPE_NS = 135
ND_TYPE_NA = 136


class LoND(threading.Thread):
    def __init__(self, ufc, node, iomap, times = -1, interval = 30):
        
        self.ports = {
            'lo_service': {'dir': 'out', 'type': 'service'},
            'lo_up2down': {'dir': 'out', 'type': 'topic'},
            'IA135_ns': {'dir': 'in', 'type': 'topic',
                    'callback': self.lo_down2up, 'data_type': bytes},
            'IA136_na': {'dir': 'in', 'type': 'topic',
                    'callback': self.lo_down2up, 'data_type': bytes}
        }
        
        self.times = times
        self.interval = interval
        self.state = 'IDLE' if times == 0 else 'BEGIN'
        self.identify = randint(0, 0xffffffff)
        self.if_get_self = False
        self.evt = threading.Event()
        
        self.node = node
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        ufc.node_init(node, self.ports, iomap)
        
        self.mac = self.get_intf_mac()
        if self.mac == None:
            return

        threading.Thread.__init__(self)
        self.daemon = True
        self.alive = True
        self.start()
    
    def get_intf_mac(self):
        ret = self.ports['lo_service']['handle'].call('get mac')
        if ret.startswith('ok, '):
            return int(ret[4:], 16)
        else:
            self.logger.error('get_intf_mac failed: ' + ret)
            return None
    
    def run(self):
        while self.alive:
            if self.state == 'BEGIN':
                self.target_mac = randint(0, 254) if self.mac == 255 else self.mac
                self.identify = randint(0, 0xffffffff)
                if self.mac == 255:
                    ret = self.ports['lo_service']['handle'].call('set filter %02x' % self.target_mac)
                    if not ret.startswith('ok'):
                        self.logger.error('set filter failed: ' + ret)
                self.state = 'SEND_NS'
            if self.state == 'SEND_NS':
                self.logger.log(logging.VERBOSE, 'send ns...')
                packet = LoCD.new_message()
                packet.srcAddrType = LO_ADDR_UNSP
                packet.srcMac = 255
                packet.dstAddrType = LO_ADDR_LL0
                packet.dstMac = self.target_mac
                packet.init('icmp')
                packet.icmp.type = ND_TYPE_NS
                packet.data = self.identify.to_bytes(6, 'little')
                data = packet.to_bytes_packed()
                self.evt.clear()
                self.if_get_self = False
                self.state = 'WAIT_RX'
                self.ports['lo_up2down']['handle'].publish(data)
            if self.state == 'WAIT_RX':
                self.evt.wait(timeout = 0.5) # wait timeout
                if self.state == 'WAIT_RX':
                    if self.if_get_self:
                        self.logger.debug('keep or update mac')
                        if self.mac == 255:
                            self.mac = self.target_mac
                            ret = self.ports['lo_service']['handle'].call('set mac %02x' % self.mac)
                            if ret != 'ok':
                                self.logger.error('set mac: failed: ' + ret)
                        self.state = 'IDLE'
                    else:
                        self.logger.debug('re SEND_NS')
                        self.state = 'SEND_NS'
            if self.state == 'IDLE':
                if self.times > 0:
                    self.times -= 1
                sleep(self.interval)
                if self.times != 0:
                    self.logger.debug('start next ND, times: %d' % self.times)
                    self.state = 'BEGIN'
        
        self.com.close()
    
    def stop(self):
        self.alive = False
        self.join()
    
    
    def lo_down2up(self, msg):
        packet = LoCD.from_bytes_packed(msg)
        if packet.icmp.type == ND_TYPE_NS:
            if self.mac != 255 and (self.state != 'WAIT_RX' or
                    packet.data != self.identify.to_bytes(6, 'little')):
                packet = LoCD.new_message()
                packet.srcAddrType = LO_ADDR_UNSP
                packet.srcMac = 255
                packet.dstAddrType = LO_ADDR_LL0
                packet.dstMac = self.mac
                packet.init('icmp')
                packet.icmp.type = ND_TYPE_NA
                packet.data = self.identify.to_bytes(6, 'little') + b'\x00'
                data = packet.to_bytes_packed()
                self.ports['lo_up2down']['handle'].publish(data)
            if self.state != 'WAIT_RX':
                return
            if packet.data == self.identify.to_bytes(6, 'little'):
                self.if_get_self = True
            else:
                if self.mac == 255:
                    self.state = 'BEGIN'
                    self.evt.set() # kick
            
        elif packet.icmp.type == ND_TYPE_NA:
            if self.state != 'WAIT_RX':
                return
            if self.mac == 255:
                self.state = 'BEGIN'
                self.evt.set() # kick
            elif packet.data[:6] != self.identify.to_bytes(6, 'little'):
                self.mac = 255
                ret = self.ports['lo_service']['handle'].call('set mac ff')
                if ret != 'ok':
                    self.logger.error('set mac ff: failed: ' + ret)
                else:
                    self.logger.error('set mac to: 255')
                self.state = 'BEGIN'
                self.evt.set() # kick


