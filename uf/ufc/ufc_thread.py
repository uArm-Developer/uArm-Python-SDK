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


class TopicSub(threading.Thread):
    def __init__(self, node, topic, callback, queue_size, allow_drop):
        self.node = node
        self.topic = topic
        self.callback = callback
        self.allow_drop = allow_drop
        self.queue = Queue(queue_size)
        threading.Thread.__init__(self)
        self.daemon = True
        self.alive = True
        self.start()
    
    def run(self):
        while self.alive:
            self.callback(self.queue.get())
    
    def stop(self):
        self.alive = False
        self.join()

class TopicPub():
    def __init__(self, node, topic):
        self.node = node
        self.topic = topic
    
    def publish(self, message):
        # TODO: check for allow_drop
        for _, item in self.topic.subs.items():
            item.queue.put(message)

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
    def __init__(self, node, service, callback):
        self.node = node
        self.service = service
        self.callback = callback

class ServiceReq():
    def __init__(self, node, service):
        self.node = node
        self.service = service
    
    def call(self, message):
        ret = self.service.provider.callback(message)
        return ret if ret != None else ''

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
    
    def topic_subscriber(self, node, path, callback, queue_size = 100, allow_drop = True):
        b = self._get_bus(path, ctype = Topic)
        i = TopicSub(node, b, callback, queue_size = queue_size, allow_drop = allow_drop)
        b.add_sub(i)
        return i
    
    def topic_publisher(self, node, path):
        b = self._get_bus(path, ctype = Topic)
        i = TopicPub(node, b)
        b.add_pub(i)
        return i
    
    def service_register(self, node, path, callback):
        b = self._get_bus(path, ctype = Service)
        i = ServiceProvider(node, b, callback = callback)
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


