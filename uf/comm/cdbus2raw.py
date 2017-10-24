#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>
#
# CDBUS2RAW is a slave hardware module provide
# connectivity between CDBUS and other UART protocols

import threading
import queue
from time import sleep

from .locd.locd_serdes import LoCD
from .locd.locd import *
from ..utils.log import *

class Cdbus2Raw(threading.Thread):
    def __init__(self, ufc, node, iomap, listen_port, by_line = True,
                 dev_filter = 'M: cdbus2raw'):
        
        self.ports = {
            'service':      {'dir': 'in', 'type': 'service', 'callback': self.service_cb},
            'raw_up2down':  {'dir': 'in', 'type': 'topic',
                             'callback': self.raw_up2down_cb, 'data_type': bytes},
            'raw_down2up':  {'dir': 'out', 'type': 'topic'},
            
            'lo_service':   {'dir': 'out', 'type': 'service'},
            'RV_socket':    {'dir': 'out', 'type': 'topic'},
            'RA_socket':    {'dir': 'in', 'type': 'topic',
                             'callback': self.RA_socket_cb, 'data_type': bytes},
            'SA_listen':    {'dir': 'in', 'type': 'topic',
                             'callback': self.SA_listen_cb, 'data_type': bytes}
        }
        
        self.by_line = by_line
        self.line_buffer = b''
        self.dev_filter = dev_filter
        self.listen_port = listen_port
        self.dev_state = 'BEGIN' # 'UNCONNECT', 'CONNECTED', 'CONFIGURED'
        self.pc_mac = 0xff
        self.dev_site = 0
        self.dev_ip = 0xff
        self.dev_local_mac = 0xff
        self.dev_report_mac = 0xff
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
                    self.logger.info('dev info: ' + ''.join(map(chr, packet.data)))
                    self.dev_state = 'CONNECTED'
            
            if self.dev_state == 'CONNECTED':
                if self.dev_site != 0:
                    # TODO:
                    # check for report_mac
                    # self.dev_report_mac = xxx
                    self.logger.error('unsupport dev_site != 0 at now')
                else:
                    self.dev_report_mac = self.pc_mac
                
                packet = LoCD.new_message()
                packet.udp.dstPort = 2000
                packet.dstMac = self.dev_local_mac
                if self.dev_site == 0:
                    packet.dstAddrType = LO_ADDR_LL0
                    packet.data = self.dev_report_mac.to_bytes(1, 'big') + self.listen_port.to_bytes(2, 'big') + \
                                  (LO_ADDR_LL0).to_bytes(1, 'big') + b'\x00' * 16
                else:
                    packet.dstAddrType = LO_ADDR_UGC16
                    packet.dstAddr = b'\x00' * 15 + self.dev_ip.to_bytes(1, 'big')
                    packet.data = self.dev_report_mac.to_bytes(1, 'big') + self.listen_port.to_bytes(2, 'big') + \
                                  (LO_ADDR_UGC16).to_bytes(1, 'big') + \
                                  b'\x00' * 15 + self.pc_mac.to_bytes(1, 'big') # site: 0
                data = packet.to_bytes_packed()
                self.ans_pkts.queue.clear()
                self.ports['RV_socket']['handle'].publish(data)
                try:
                    ret_frame = self.ans_pkts.get(timeout = 0.5)
                    self.logger.info('configure dev done')
                    self.dev_state = 'CONFIGURED'
                except queue.Empty:
                    self.logger.error('set report no answer, disconnected...')
                    self.dev_state = 'UNCONNECT'
            
            if self.dev_state == 'CONFIGURED':
                sleep(1)
                # TODO: checking connectivity by period
    
    def stop(self):
        self.alive = False
        self.join()
    
    def RA_socket_cb(self, msg):
        packet = LoCD.from_bytes_packed(msg)
        self.ans_pkts.put(packet)
    
    def SA_listen_cb(self, msg):
        packet = LoCD.from_bytes_packed(msg)
        if self.by_line:
            self.line_buffer += packet.data
            if not packet.data.endswith(b'\n'):
                return
            for line in self.line_buffer.splitlines():
                self.logger.log(logging.VERBOSE, '-> {}'.format(line))
                self.ports['raw_down2up']['handle'].publish(line)
            self.line_buffer = b''
        else:
            self.logger.log(logging.VERBOSE, '-> {}'.format(packet.data))
            self.ports['raw_down2up']['handle'].publish(packet.data)
    
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
        self.logger.log(logging.VERBOSE, '<- {}'.format(packet.data))
        self.ports['RV_socket']['handle'].publish(data)
    
    def service_cb(self, msg):
        msg = msg.split(' ', 2)
        
        if msg[1] == 'state':
            if msg[0] == 'get':
                ret = 'ok, ' + self.dev_state
                self.logger.debug('get state ret: %s' % ret)
                return ret


