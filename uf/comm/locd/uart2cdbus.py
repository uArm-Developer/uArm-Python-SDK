#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>
#
# The UART2CDBUS hardware module converts CDBUS frame between UART and RS485
# The module has two address:
#   0x55: check module info, set/get module settings
#   0x56: data transparent transmission

import queue

from .locd_serdes import LoCD
from .locd import *
from ...utils.log import *


class Uart2Cdbus():
    def __init__(self, ufc, node, iomap, mac = 255):
        
        self.ports = {
            'service': {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            
            'lo_down2up': {'dir': 'out', 'type': 'topic'},
            'lo_up2down': {'dir': 'in', 'type': 'topic',
                    'callback': self.lo_up2down, 'data_type': bytes},
            'lo_up2down_repl_src': {'dir': 'in', 'type': 'topic',
                    'callback': self.lo_up2down_repl_src, 'data_type': bytes},
            'lo_up2down_xchg': {'dir': 'in', 'type': 'topic',
                    'callback': self.lo_up2down_xchg, 'data_type': bytes},
            
            #'cd_service': {'dir': 'out', 'type': 'service'},
            'cd_up2down': {'dir': 'out', 'type': 'topic'},
            'cd_down2up': {'dir': 'in', 'type': 'topic',
                    'callback': self.cd_down2up, 'data_type': bytes}
        }
        
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        self.site = 0
        self.mac = mac
        self.gate_ans = queue.Queue(1)
        ufc.node_init(node, self.ports, iomap)
        
        ret = self.gate_command(1000, b'')
        if ret != None:
            self.logger.info('dev info: ' + ''.join(map(chr, ret)))
        else:
            raise Exception('get dev info failed')
    
    def gate_command(self, port, data):
        packet = LoCD.new_message()
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
            self.logger.error('gate_command no answer')
            return None
        ret_packet = lo_from_frame(ret_frame)
        if ret_packet.udp.srcPort != port:
            self.logger.error('gate_command wrong answer port')
            return None
        return ret_packet.data
    
    def gate_setting(self, msg):
        msg = msg.split(' ', 2)
        
        if msg[1] == 'info':
            if msg[0] == 'get':
                ret = self.gate_command(1000, b'')
                if ret != None:
                    return 'ok, ' + ''.join(map(chr, ret))
                else:
                    return 'err'
        if msg[1] == 'filter':
            if msg[0] == 'set':
                data = int(msg[2], 16).to_bytes(1, 'little')
                ret = self.gate_command(2000, data)
                if ret == b'':
                    return 'ok'
                else:
                    return 'err'
    
    def local_setting(self, msg):
        msg = msg.split(' ', 2)
        
        if msg[1] == 'mac':
            if msg[0] == 'get':
                return 'ok, ' + '%02x' % self.mac
            if msg[0] == 'set':
                self.mac = int(msg[2], 16)
                return 'ok'
        if msg[1] == 'site':
            if msg[0] == 'get':
                return 'ok, ' + '%02x' % self.site
            if msg[0] == 'set':
                self.site = int(msg[2], 16)
                return 'ok'
    
    def lo_send_packet(self, packet):
        if self.mac == 255 and packet.which() == 'udp':
            self.logger.error('send udp is not allowd if mac == 255')
            return
        frame = lo_to_frame(packet)
        frame = b'\xaa\x56' + len(frame).to_bytes(1, 'little') + frame
        self.ports['cd_up2down']['handle'].publish(frame)
    
    def lo_up2down(self, msg):
        packet = LoCD.from_bytes_packed(msg)
        self.lo_send_packet(packet)
    
    def lo_up2down_repl_src(self, msg):
        packet = LoCD.from_bytes_packed(msg).as_builder()
        lo_fill_src_addr(self, packet)
        self.lo_send_packet(packet)
    
    def lo_up2down_xchg(self, msg):
        packet = LoCD.from_bytes_packed(msg).as_builder()
        lo_exchange_src_dst(self, packet)
        self.lo_send_packet(packet)
    
    def cd_down2up(self, msg):
        if msg.startswith(b'\x56\xaa'):
            packet = lo_from_frame(msg[3:])
            if self.mac == 255 and packet.which() == 'udp':
                return
            data = packet.to_bytes_packed()
            self.ports['lo_down2up']['handle'].publish(data)
        elif msg.startswith(b'\x55\xaa'):
            self.gate_ans.queue.clear()
            self.gate_ans.put(msg)
    
    def service_cb(self, msg):
        if msg.startswith('get info') or msg.startswith('set filter'):
            return self.gate_setting(msg)
        if msg.find(' mac')  == 3 or msg.find(' site') == 3:
            return self.local_setting(msg)


