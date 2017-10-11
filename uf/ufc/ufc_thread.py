#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from queue import Queue
import _thread, threading
from .ufc import UFC


def case_to_type(dst_type, data):
    assert dst_type == str or dst_type == bytes
    assert isinstance(data, str) or isinstance(data, bytes)
    if isinstance(data, dst_type):
        return data
    if isinstance(data, str):
        return bytes(map(ord, data))
    else:
        return ''.join(map(chr, data))


class TopicSub(threading.Thread):
    def __init__(self, node, topic, callback, queue_size, allow_drop, data_type):
        self.node = node
        self.topic = topic
        self.callback = callback
        self.allow_drop = allow_drop
        self.data_type = data_type
        self.queue = Queue(queue_size)
        threading.Thread.__init__(self)
        self.daemon = True
        self.alive = True
        self.start()
    
    def run(self):
        while self.alive:
            msg = self.queue.get()
            msg = case_to_type(self.data_type, msg)
            self.callback(msg)
    
    def stop(self):
        self.alive = False
        self.join()

class TopicPub():
    def __init__(self, node, topic):
        self.node = node
        self.topic = topic
    
    def publish(self, msg):
        # TODO: check for allow_drop
        for _, item in self.topic.subs.items():
            assert isinstance(msg, str) or isinstance(msg, bytes)
            item.queue.put(msg)

class Topic():
    def __init__(self, path):
        self.path = path
        self.subs = {} # format: 'node: handle, ...'
        self.pubs = {}
        #self.pub_lock = _thread.allocate_lock()
        
    def add_sub(self, handle):
        self.subs[handle.node] = handle
    
    def add_pub(self, handle):
        self.pubs[handle.node] = handle


class ServiceProvider():
    def __init__(self, node, service, callback, data_type):
        self.node = node
        self.service = service
        self.callback = callback
        self.data_type = data_type

class ServiceReq():
    def __init__(self, node, service):
        self.node = node
        self.service = service
    
    def call(self, msg):
        assert isinstance(msg, str) or isinstance(msg, bytes)
        req_type = type(msg)
        msg = case_to_type(self.service.provider.data_type, msg)
        ret = self.service.provider.callback(msg)
        if ret == None:
            ret = b''
        return case_to_type(req_type, ret)

class Service():
    def __init__(self, path):
        self.path = path
        self.provider = None
        self.reqs = {}
        
    def add_provider(self, handle):
        if self.provider:
            raise Exception('already registered')
        self.provider = handle
    
    def add_req(self, handle):
        self.reqs[handle.node] = handle




class UFCThread(UFC):
    '''Inner-Thread communication provider for UFC'''
    def __init__(self):
        self._buses = {} # format: 'path: handle, ...'
    
    def topic_subscriber(self, node, path, callback, queue_size = 100, allow_drop = True, data_type = str):
        b = self._get_bus(path, ctype = Topic)
        i = TopicSub(node, b, callback, queue_size = queue_size, allow_drop = allow_drop, data_type = data_type)
        b.add_sub(i)
        return i
    
    def topic_publisher(self, node, path):
        b = self._get_bus(path, ctype = Topic)
        i = TopicPub(node, b)
        b.add_pub(i)
        return i
    
    def service_register(self, node, path, callback, data_type = str):
        b = self._get_bus(path, ctype = Service)
        i = ServiceProvider(node, b, callback = callback, data_type = data_type)
        b.add_provider(i)
        return i
    
    def service_proxy(self, node, path):
        b = self._get_bus(path, ctype = Service)
        i = ServiceReq(node, b)
        b.add_req(i)
        return i
    
    def _get_bus(self, path, ctype = Topic):
        if path not in self._buses.keys():
            self._buses[path] = ctype(path)
        return self._buses[path]


