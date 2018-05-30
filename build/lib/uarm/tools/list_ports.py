#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

from serial.tools import list_ports
from .config import UARM_PROPERTY


def get_ports(filters=None):
    ports = []
    for i in list_ports.comports():
        if i.pid is not None:
            is_match = True
            if isinstance(filters, dict):
                for k, v in filters.items():
                    if not hasattr(i, k):
                        continue
                    a = getattr(i, k)
                    if not a:
                        a = ''
                    if a.find(v) == -1:
                        is_match = False
                        break
            if is_match:
                ports.append({
                    'pid': '{:04x}'.format(i.pid),
                    'vid': '{:04x}'.format(i.vid),
                    'device': i.device,
                    'serial_number': i.serial_number,
                    'hwid': i.hwid,
                    'name': i.name,
                    'description': i.description,
                    'interface': i.interface,
                    'location': i.location,
                    'manufacturer': i.manufacturer,
                    'product': i.product
                })
    return ports


def select_port(filters, connect_ports=[]):
    port = None
    for i in list_ports.comports():
        if i.pid is None:
            continue
        if i.device in connect_ports:
            continue
        if not isinstance(filters, dict):
            port = i.device
            break
        is_match = True
        for k, v in filters.items():
            if not hasattr(i, k):
                continue
            a = getattr(i, k)
            if not a:
                a = ''
            if a.find(v) == -1:
                is_match = False
                break
        if is_match:
            port = i.device
            break
    return port


UARM_HWID_KEYWORD = set()
for c in UARM_PROPERTY.keys():
    UARM_HWID_KEYWORD.add("{}:{}".format(UARM_PROPERTY[c]['vid'], UARM_PROPERTY[c]['pid']))


def filter_uarm_ports():
    uarm_ports = []
    for i in list_ports.comports():
        if i.pid is None:
            continue
        for h in UARM_HWID_KEYWORD:
            if "{}:{}".format("{:04x}".format(i.vid), "{:04x}".format(i.pid)) == h:
                uarm_ports.append(i[0])
    return uarm_ports

