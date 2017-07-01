#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


class UFC():
    '''\
    Communication wrapper for uFactory
    '''
    
    def node_init(self, node, ports, iomap):
        '''\
        
        ports = {
            'in': {'dir': 'in', 'type': 'topic', 'callback': self.io_in_cb},
            'out': {'dir': 'out', 'type': 'topic'},
            'service': {'dir': 'in', 'type': 'service', 'callback': self.io_service_cb}
        }
        
        iomap = {
            'out': 'PATH/TO/BUS',
            'service': 'PATH/TO/BUS'
        }
        
        '''
        
        for k, item in ports.items():
            item['handle'] = None
        
        for k, path in iomap.items():
            if ports[k]['type'] == 'topic':
                if ports[k]['dir'] == 'in':
                    # TODO: set queue_size and allow_drop
                    ports[k]['handle'] = self.topic_subscriber(node, path, ports[k]['callback'])
                elif ports[k]['dir'] == 'out':
                    ports[k]['handle'] = self.topic_publisher(node, path)
            elif ports[k]['type'] == 'service':
                if ports[k]['dir'] == 'in':
                    ports[k]['handle'] = self.service_register(node, path, ports[k]['callback'])
                elif ports[k]['dir'] == 'out':
                    ports[k]['handle'] = self.service_proxy(node, path)


