#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

try:
    import capnp
    from .locd_capnp import LoCD
    
except ModuleNotFoundError:
    import json
    
    class LoCD():
    
        class UdpMsg():
            def __init__(self):
                self.srcPort = 0
                self.dstPort = 0
            def __repr__(self):
                return 'LoCD.UdpMsg(): {}'.format(self.__dict__)
        
        class IcmpMsg():
            def __init__(self):
                self.type = 0
            def __repr__(self):
                return 'LoCD.IcmpMsg(): {}'.format(self.__dict__)
        
        class LocdMsg():
            def __init__(self):
                self.srcAddrType = 0
                self.srcAddr = b''
                self.srcMac = 0
                
                self.dstAddrType = 0
                self.dstAddr = b''
                self.dstMac = 0
                
                self.udp = LoCD.UdpMsg()
                self.icmp = None
                
                self.data = b''
            
            def which(self):
                if self.udp != None:
                    return 'udp'
                else:
                    return 'icmp'
            
            def init(self, value):
                if value == 'udp':
                    self.udp = LoCD.UdpMsg()
                    self.icmp = None
                elif value == 'icmp':
                    self.udp = None
                    self.icmp = LoCD.IcmpMsg()
                else:
                    raise Exception('wrong value')
            
            def as_builder(self):
                return self
            
            def to_bytes_packed(self):
                if not isinstance(self.srcAddr, bytes):
                    self.srcAddr = bytes(map(ord, self.srcAddr))
                if not isinstance(self.dstAddr, bytes):
                    self.dstAddr = bytes(map(ord, self.dstAddr))
                if not isinstance(self.data, bytes):
                    self.data = bytes(map(ord, self.data))
                return json.dumps(self.__dict__, default = LoCD.to_json)
            
            def __repr__(self):
                return 'LoCD.LocdMsg(): {}'.format(self.__dict__)
        
        @staticmethod
        def from_bytes_packed(msg):
            self = LoCD.new_message()
            entries = json.loads(msg)
            self.__dict__.update(entries)
            if 'udp' in entries and entries['udp'] != None:
                self.udp = LoCD.UdpMsg()
                self.udp.__dict__.update(entries['udp'])
                self.icmp = None
            elif 'icmp' in entries and entries['icmp'] != None:
                self.udp = None
                self.icmp = LoCD.IcmpMsg()
                self.icmp.__dict__.update(entries['icmp'])
            else:
                raise Exception('wrong value')
            
            if len(self.srcAddr) != 0:
                self.srcAddr = bytes([int(i, 16) for i in self.srcAddr.split(' ')])
            else:
                self.srcAddr = b''
            
            if len(self.dstAddr) != 0:
                self.dstAddr = bytes([int(i, 16) for i in self.dstAddr.split(' ')])
            else:
                self.dstAddr = b''
            
            if len(self.data) != 0:
                self.data = bytes([int(i, 16) for i in self.data.split(' ')])
            else:
                self.data = b''
            
            return self
        
        @staticmethod
        def to_json(python_object):
            if isinstance(python_object, bytes):
                return ' '.join('%02x' % b for b in python_object)
            
            if isinstance(python_object, LoCD.UdpMsg):
                return python_object.__dict__
            
            if isinstance(python_object, LoCD.IcmpMsg):
                return python_object.__dict__
            
            raise TypeError(repr(python_object) + ' is not JSON serializable')
        
        @staticmethod
        def new_message():
            return LoCD.LocdMsg()


