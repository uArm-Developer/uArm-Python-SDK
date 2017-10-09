#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

import queue
import capnp

import locd_capnp
from .locd import *
from ...utils.log import *

class Uart2Cdbus():
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            
            'lo_down2up': {'dir': 'out', 'type': 'topic'},
            'lo_up2down': {'dir': 'in', 'type': 'topic', 'callback': self.lo_up2down, 'data_type': bytes},
            
            #'cd_service': {'dir': 'out', 'type': 'service'},
            'cd_up2down': {'dir': 'out', 'type': 'topic'},
            'cd_down2up': {'dir': 'in', 'type': 'topic', 'callback': self.cd_down2up, 'data_type': bytes}
        }
        
        self.logger = logging.getLogger(node)
        self.site = 0
        self.mac = 255
        self.gate_ans = queue.Queue(1)
        ufc.node_init(node, self.ports, iomap)
    
    def gate_command(self, port, data):
        packet = locd_capnp.LoCD.new_message()
        packet.init('udp')
        
        packet.srcAddrType = LO_ADDR_LL0
        packet.srcMac = 0xaa
        packet.dstAddrType = LO_ADDR_LL0
        packet.dstMac = 0x55
        
        packet.udp.srcPort = 0xf000
        packet.udp.dstPort = port
        packet.data = data
        
        frame = lo_to_frame(packet)
        
        self.gate_ans.queue.clear()
        self.ports['cd_up2down']['handle'].publish(frame)
        try:
            ret_frame = self.gate_ans.get(timeout = 0.5)
        except queue.Empty:
            return None
        ret_packet = lo_from_frame(ret_frame)
        if ret_packet.udp.srcPort != port:
            return None
        return ret_packet.data
    
    def gate_setting(self, msg):
        words = msg.split(' ', 1)
        action = words[0]
        
        words = words[1].split(' ', 1)
        param = words[0]
        
        if param == 'info':
            if action == 'get':
                ret = self.gate_command(1000, None)
                if ret != None:
                    return 'ok, ' + ''.join(map(chr, ret))
                else:
                    return 'err'
        if param == 'filter':
            if action == 'set':
                data = int(words[1], 16).to_bytes(1, 'little')
                ret = self.gate_command(2000, data)
                if ret == b'':
                    return 'ok'
                else:
                    return 'err'
    
    def local_setting(self, msg):
        words = msg.split(' ', 1)
        action = words[0]
        
        words = words[1].split(' ', 1)
        param = words[0]
        
        if param == 'mac':
            if action == 'get':
                return 'ok, ' + '%02x' % self.mac
            if action == 'set':
                self.mac = int(words[1], 16)
                return 'ok'
        if param == 'site':
            if action == 'get':
                return 'ok, ' + '%02x' % self.site
            if action == 'set':
                self.site = int(words[1], 16)
                return 'ok'
    
    def lo_up2down(self, msg):
        packet = locd_capnp.LoCD.from_bytes_packed(msg)
        frame = lo_to_frame(packet)
        frame = b'\xaa\x56' + len(frame).to_bytes(1, 'little') + frame
        self.ports['cd_up2down']['handle'].publish(frame)
    
    def cd_down2up(self, msg):
        if msg.startswith(b'\x56\xaa'):
            packet = lo_from_frame(msg[3:])
            self.ports['lo_down2up']['handle'].publish(frame)
        elif msg.startswith(b'\x55\xaa'):
            self.gate_ans.queue.clear()
            self.gate_ans.put(frame)
    
    def service_cb(self, msg):
        if msg.startswith('get info') or msg.startswith('set filter'):
            return gate_setting(msg)
        if msg.find(' mac')  == 3 or msg.find(' site') == 3:
            return local_setting(msg)


