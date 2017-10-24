#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>
#
# 6LoCD:
#   Compression Format for IPv6 Datagrams over CDBUS, depends on 6LoWPAN.

import struct

from .locd_serdes import LoCD
from ...utils.log import *

LO_ADDR_LL0     = 0x3
LO_ADDR_UGC16   = 0x6
LO_ADDR_UG128   = 0x0
LO_ADDR_UNSP    = 0x4
LO_ADDR_M8      = 0xb
LO_ADDR_M32     = 0xa
LO_ADDR_M128    = 0x8

LO_NH_UDP       = 0xf4 # C = 'b1
LO_NH_ICMP      = 0xf8


def lo_to_frame(packet):
    header = b''
    header += packet.srcMac.to_bytes(1, 'little')
    header += packet.dstMac.to_bytes(1, 'little')
    
    payload = b'\x7f'
    payload += (packet.srcAddrType << 4 | packet.dstAddrType).to_bytes(1, 'big')
    
    if packet.srcAddrType == LO_ADDR_UNSP:
        assert packet.srcMac == 0xff
    elif packet.srcAddrType == LO_ADDR_LL0:
        assert packet.srcMac != 0xff
    elif packet.srcAddrType == LO_ADDR_UGC16:
        payload += packet.srcAddr[7:8]
        payload += packet.srcAddr[15:16]
        assert packet.srcMac != 0xff
    elif packet.srcAddrType == LO_ADDR_UG128:
        payload += packet.srcAddr
        assert len(packet.srcAddr) == 16
        assert packet.srcMac != 0xff
    else:
        assert False

    if packet.dstAddrType == LO_ADDR_LL0:
        assert packet.dstMac != 0xff
    elif packet.dstAddrType == LO_ADDR_UGC16:
        payload += packet.dstAddr[7:8]
        payload += packet.dstAddr[15:16]
        assert packet.dstMac != 0xff
    elif packet.dstAddrType == LO_ADDR_UG128 or \
            packet.dstAddrType == LO_ADDR_M128:
        payload += packet.dstAddr
        assert len(packet.dstAddr) == 16
    elif packet.dstAddrType == LO_ADDR_M8:
        payload += packet.dstAddr[15:16]
    elif packet.dstAddrType == LO_ADDR_M32:
        payload += packet.dstAddr[1:2]
        payload += packet.dstAddr[13:16]
    else:
        assert False

    if packet.which() == 'udp':
        udp_h1 = LO_NH_UDP
        udp_h2 = b''
        if packet.udp.srcPort >> 8 == 0xf0:
            udp_h1 |= 0x2
            udp_h2 += (packet.udp.srcPort & 0xff).to_bytes(1, 'big')
        else:
            udp_h2 += packet.udp.srcPort.to_bytes(2, 'big')
        
        if packet.udp.dstPort >> 8 == 0xf0:
            udp_h1 |= 0x1
            udp_h2 += (packet.udp.dstPort & 0xff).to_bytes(1, 'big')
        else:
            udp_h2 += packet.udp.dstPort.to_bytes(2, 'big')
        
        payload += udp_h1.to_bytes(1, 'big') + udp_h2
    
    elif packet.which() == 'icmp':
        payload += LO_NH_ICMP.to_bytes(1, 'big')
        payload += packet.icmp.type.to_bytes(1, 'big')
    else:
        assert False

    payload += packet.data if isinstance(packet.data, bytes) \
                           else bytes(map(ord, packet.data))
    frame = header + len(payload).to_bytes(1, 'little') + payload
    assert len(frame) <= 256
    return frame


def lo_from_frame(frame):
    packet = LoCD.new_message()
    
    packet.srcMac = frame[0]
    packet.dstMac = frame[1]
    remains = frame[3:]
    
    assert remains[0] == 0x7f
    packet.srcAddrType = remains[1] >> 4
    packet.dstAddrType = remains[1] & 0xf
    remains = remains[2:]

    if packet.srcAddrType == LO_ADDR_UNSP:
        assert packet.srcMac == 0xff
    elif packet.srcAddrType == LO_ADDR_LL0:
        assert packet.srcMac != 0xff
    elif packet.srcAddrType == LO_ADDR_UGC16:
        packet.srcAddr = b'\x00' * 7 + remains[0:1] + b'\x00' * 7 + remains[1:2]
        remains = remains[2:]
        assert packet.srcMac != 0xff
    elif packet.srcAddrType == LO_ADDR_UG128:
        packet.srcAddr = remains[0:16]
        remains = remains[16:]
    else:
        assert False

    if packet.dstAddrType == LO_ADDR_LL0:
        assert packet.dstMac != 0xff
    elif packet.dstAddrType == LO_ADDR_UGC16:
        packet.dstAddr = b'\x00' * 7 + remains[0:1] + b'\x00' * 7 + remains[1:2]
        remains = remains[2:]
        assert packet.dstMac != 0xff
    elif packet.dstAddrType == LO_ADDR_UG128 or \
            packet.dstAddrType == LO_ADDR_M128:
        packet.dstAddr = remains[0:16]
        remains = remains[16:]
    elif packet.dstAddrType == LO_ADDR_M8:
        packet.dstAddr = b'\x00' * 15 + remains[0:1]
        remains = remains[1:]
    elif packet.dstAddrType == LO_ADDR_M32:
        packet.dstAddr = remains[0:1] + b'\x00' * 12 + remains[1:4]
        remains = remains[4:]
    else:
        assert False

    if (remains[0] & 0xfc) == LO_NH_UDP:
        packet.init('udp')
        pkt_type = remains[0]
        remains = remains[1:]

        if pkt_type & 0x2:
            packet.udp.srcPort = 0xf000 | (remains[0] & 0xff)
            remains = remains[1:]
        else:
            packet.udp.srcPort = struct.unpack(">H", remains[0:2])[0]
            remains = remains[2:]
        
        if pkt_type & 0x1:
            packet.udp.dstPort = 0xf000 | (remains[0] & 0xff)
            remains = remains[1:]
        else:
            packet.udp.dstPort = struct.unpack(">H", remains[0:2])[0]
            remains = remains[2:]

    elif remains[0] == LO_NH_ICMP:
        packet.init('icmp')
        packet.icmp.type = remains[1]
        remains = remains[2:]
    else:
        assert False
    
    packet.data = remains
    return packet


# helper

def lo_exchange_src_dst(intf, packet):
    packet.udp.srcPort, packet.udp.dstPort = packet.udp.dstPort, packet.udp.srcPort
    packet.srcAddrType, packet.dstAddrType = packet.dstAddrType, packet.srcAddrType
    packet.srcAddr, packet.dstAddr = packet.dstAddr, packet.srcAddr
    packet.srcMac, packet.dstMac = packet.dstMac, packet.srcMac

    if packet.dstAddrType == LO_ADDR_UNSP:
        packet.dstAddrType = LO_ADDR_M8
        packet.dstAddr[15] = b'\x00' * 15 + b'\x01'
        packet.dstMac = 0xff

    if packet.srcAddrType & 0x8:
        if packet.srcAddrType == LO_ADDR_M8:
            packet.srcAddrType = LO_ADDR_LL0
        elif packet.srcAddrType == LO_ADDR_M32 or packet.srcAddrType == LO_ADDR_M128:
            packet.srcAddrType = LO_ADDR_UGC16
            packet.srcAddr = b'\x00' * 7 + intf.site.to_bytes(1, 'big') + \
                             b'\x00' * 7 + intf.mac.to_bytes(1, 'big')
        lo_pkt.srcMac = intf.mac


def lo_fill_src_addr(intf, packet):
    if packet.dstAddrType == LO_ADDR_LL0 or packet.dstAddrType == LO_ADDR_M8:
        packet.srcAddrType = LO_ADDR_LL0
        packet.srcMac = intf.mac
    else:
        packet.srcAddrType = LO_ADDR_UGC16
        packet.srcAddr = b'\x00' * 7 + intf.site.to_bytes(1, 'big') + \
                         b'\x00' * 7 + intf.mac.to_bytes(1, 'big')
        packet.srcMac = intf.mac


