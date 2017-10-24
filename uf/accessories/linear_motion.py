#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>
#
# For conveyor belt and slide rail

import threading
import queue
import struct
from time import sleep

from ..comm.locd.locd_serdes import LoCD
from ..comm.locd.locd import *
from ..utils.log import *

class LinearMotion(threading.Thread):
    def __init__(self, ufc, node, iomap, dev_filter = 'M: uf_slide'):
        
        self.ports = {
            'service':      {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            #'pos_in':      {'dir': 'in', 'type': 'topic', 'callback': self.pos_in_cb},
            
            'lo_service':   {'dir': 'out', 'type': 'service'},
            'RV_socket':    {'dir': 'out', 'type': 'topic'},
            'RA_socket':    {'dir': 'in', 'type': 'topic',
                             'callback': self.RA_socket_cb, 'data_type': bytes}
        }
        
        self.dev_filter = dev_filter
        self.dev_state = 'BEGIN' # 'UNCONNECT', 'CONNECTED', 'CONFIGURED'
        self.dev_site = 0
        self.dev_ip = 0xff
        self.dev_local_mac = 0xff
        self.ans_pkts = queue.Queue(10)
        self.logger = logging.getLogger('uf.' + node.replace('/', '.'))
        ufc.node_init(node, self.ports, iomap)
        
        threading.Thread.__init__(self)
        self.daemon = True
        self.alive = True
        self.start()
    
    def run(self):
        while self.alive:
            if self.dev_state == 'BEGIN':
                pc_mac = self.ports['lo_service']['handle'].call('get mac')
                if pc_mac.startswith('ok') and pc_mac[-2:] != 'ff':
                    self.pc_mac = int(pc_mac[-2:], 16)
                    # pc_site always 0
                    self.logger.debug('pc intf ready %02x' % self.pc_mac)
                    self.dev_state = 'UNCONNECT'
                else:
                    sleep(1)
            
            if self.dev_state == 'UNCONNECT':
                packet = LoCD.new_message()
                packet.dstMac = 0xff
                packet.dstAddrType = LO_ADDR_M32
                packet.dstAddr = b'\x00\x05' + b'\x00' * 13 + b'\x01' # ff05::01
                packet.udp.dstPort = 1000
                packet.data = self.dev_filter + '\0'
                data = packet.to_bytes_packed()
                self.ans_pkts.queue.clear()
                self.ports['RV_socket']['handle'].publish(data)
                sleep(1)
                ans_size = self.ans_pkts.qsize()
                if ans_size == 0:
                    self.logger.debug('no dev found on net')
                elif ans_size > 1:
                    self.logger.warning('multi dev found on net by filter: ' + self.dev_filter)
                    while self.ans_pkts.qsize() > 0:
                        self.logger.warning('packet: {}'.format(self.ans_pkts.get()))
                else:
                    packet = self.ans_pkts.get()
                    if packet.srcAddrType != LO_ADDR_UGC16:
                        self.logger.error('wrong srcAddrType: {}'.format(packet))
                        continue
                    self.dev_local_mac = packet.srcMac
                    self.dev_site = packet.srcAddr[7]
                    self.dev_ip = packet.srcAddr[15]
                    self.logger.info('dev found on net, mac: %02x, site: %02x, ip: %02x' %
                                     (self.dev_local_mac, self.dev_site, self.dev_ip))
                    self.dev_info = ''.join(map(chr, packet.data))
                    self.logger.info('dev info: ' + self.dev_info)
                    self.dev_state = 'CONNECTED'
            
            if self.dev_state == 'CONNECTED':
                self.logger.info('enable device...')
                ret = self.cmd_sync(2021, b'\xff')
                if ret == None:
                    self.dev_state = 'UNCONNECT'
                    continue
                
                self.logger.info('set device state...')
                ret = self.cmd_sync(2022, b'\x00')
                if ret == None:
                    self.dev_state = 'UNCONNECT'
                    continue
                
                self.logger.info('return to zero point...')
                ret = self.cmd_sync(2071, b'\x01')
                if ret == None:
                    self.dev_state = 'UNCONNECT'
                    continue
                
                if self.dev_info.startswith('M: uf_slide'):
                    if self.wait_move_stop()[:3] == 'err':
                        self.logger.error('return to zero point error.')
                        self.dev_state = 'UNCONNECT'
                        continue
                    self.logger.info('return to zero point done.')
                
                self.logger.info('set device state...')
                ret = self.cmd_sync(2022, b'\x00')
                if ret == None:
                    self.dev_state = 'UNCONNECT'
                    continue
                
                self.logger.info('configure device done')
                self.dev_state = 'CONFIGURED'
            
            if self.dev_state == 'CONFIGURED':
                sleep(1)
                # TODO: checking connectivity by period
    
    def stop(self):
        self.alive = False
        self.join()
    
    def cmd_sync(self, port, msg): # call after CONNECTED only
        packet = LoCD.new_message()
        packet.dstMac = self.dev_local_mac
        if self.dev_site == 0:
            packet.dstAddrType = LO_ADDR_LL0
        else:
            packet.dstAddrType = LO_ADDR_UGC16
            packet.dstAddr = b'\x00' * 15 + self.dev_ip.to_bytes(1, 'big')
        packet.udp.dstPort = port
        packet.data = msg
        data = packet.to_bytes_packed()
        self.ans_pkts.queue.clear()
        self.ports['RV_socket']['handle'].publish(data)
        try:
            ret_frame = self.ans_pkts.get(timeout = 0.5)
            return ret_frame.data
        except queue.Empty:
            self.logger.error('cmd_sync timeout...')
            return None
            # TODO: if error > 3 times, goto UNCONNECT or BEGIN state
    
    def get_move_state(self):
        ret = self.cmd_sync(2023, b'')
        if ret == None:
            self.logger.error('no return...')
            return 'err, no return'
        elif ret[0] != 0x80:
            self.logger.error('ret error: {}'.format(ret))
            return 'err, code: %02x' % ret[1]
        elif ret[1] == 1:
            return 'moving'
        elif ret[1] == 2:
            return 'sleep'
        elif ret[1] == 3:
            return 'pause'
        elif ret[1] == 4:
            return 'stop'
    
    def wait_move_stop(self):
        while True:
            sleep(0.1)
            ret = self.get_move_state()
            if ret == 'sleep' or ret == 'stop' or ret[:3] == 'err':
                return ret
    
    def RA_socket_cb(self, msg):
        packet = LoCD.from_bytes_packed(msg)
        self.ans_pkts.put(packet)
    
    def raw_up2down_cb(self, msg):
        if self.dev_state != 'CONFIGURED':
            self.logger.error('raw_up2down: dev not ready...')
            return
        packet = LoCD.new_message()
        packet.dstMac = self.dev_local_mac
        if self.dev_site == 0:
            packet.dstAddrType = LO_ADDR_LL0
        else:
            packet.dstAddrType = LO_ADDR_UGC16
            packet.dstAddr = b'\x00' * 15 + self.dev_ip.to_bytes(1, 'big')
        packet.udp.dstPort = 2001
        packet.data = (msg + b'\n') if self.by_line else msg
        data = packet.to_bytes_packed()
        self.ports['RV_socket']['handle'].publish(data)
    
    def service_cb(self, msg):
        msg = msg.split(' ', 2)
        
        if msg[1] == 'state':
            if msg[0] == 'get':
                if self.dev_state == 'CONFIGURED':
                    ret = 'ok, {}, {}'.format(self.dev_state, self.get_move_state())
                else:
                    ret = 'ok, ' + self.dev_state
                self.logger.debug('get state ret: %s' % ret)
                return ret
        
        if msg[1].startswith('pos'):
            if msg[0] == 'get':
                ret = self.cmd_sync(2049, b'\x01')
                if not ret or ret[0] != 0x80:
                    self.logger.error('get pos error: {}'.format(ret))
                    return 'err'
                else:
                    pos = struct.unpack("f", ret[1:])[0]
                ret = 'ok, {}'.format(pos)
                self.logger.debug('get pos ret: %s' % ret)
                return ret
            if msg[0] == 'set':
                args = msg[2].split(' ')
                pos = float(args[0])
                speed = float(args[1]) if len(args) == 2 else 10 # by default
                self.logger.debug('set {} {}, speed {}'.format(msg[1], pos, speed))
                ret = self.cmd_sync(2041, b'\x00' + bytes(struct.pack("ff", pos, speed)))
                if msg[1] == 'pos_sync':
                    ret = self.wait_move_stop()
                    return 'ok' if ret[:3] != 'err' else ret
                else:
                    return 'ok, pend: %d' % ret[-1]
        
        if msg[1] == 'pend':
            if msg[0] == 'get':
                ret = self.cmd_sync(2025, b'')
                return 'ok, pend: %d' % ret[-1]


