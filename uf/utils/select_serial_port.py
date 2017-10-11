#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from serial.tools import list_ports

def _dump_port(logger, d):
    logger.info('{}:'.format(d.device))
    logger.info('  hwid        : "{}"'.format(d.hwid))
    logger.info('  manufacturer: "{}"'.format(d.manufacturer))
    logger.info('  product     : "{}"'.format(d.product))
    logger.info('  description : "{}"'.format(d.description))

def _dump_ports(logger):
    for d in list_ports.comports():
        _dump_port(logger, d)

def select_port(logger = None, dev_port = None, filters = None, must_unique = False):
    
    if filters != None and dev_port == None:
        not_unique = False
        for d in list_ports.comports():
            is_match = True
            for k, v in filters.items():
                if not hasattr(d, k):
                    continue
                a = getattr(d, k)
                if not a:
                    a = ''
                if a.find(v) == -1:
                    is_match = False
            if is_match:
                if dev_port == None:
                    dev_port = d.device
                    if logger:
                        logger.info('choose device: ' + dev_port)
                        _dump_port(logger, d)
                else:
                    if logger:
                        logger.warning('find more than one port')
                    not_unique = True
        if not_unique:
            if logger:
                logger.info('current filter: {}, all ports:'.format(filters))
                _dump_ports(logger)
            if must_unique:
                raise Exception('port is not unique')
    
    if not dev_port:
        if logger:
            if filters:
                logger.error('port not found, current filter: {}, all ports:'.format(filters))
            else:
                logger.error('please specify dev_port or filters, all ports:')
            _dump_ports(logger)
        return None
    
    return dev_port

