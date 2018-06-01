#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFactory, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import os
import sys
import time
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI
from uarm.tools.list_ports import get_ports


"""
1. listen and auto connect all filter uArm
2. auto sync move (only enforce sync on connect a new uArm)
"""

swifts = {}
speed = 1000000
timeout = None
lock = threading.Lock()


class ListenPort(threading.Thread):
    def __init__(self):
        super(ListenPort, self).__init__()
        self.daemon = True
        self.alive = True

    def run(self):
        while self.alive:
            try:
                ports = get_ports(filters={'hwid': 'USB VID:PID=2341:0042'})
                for port in ports:
                    if port['device'] not in swifts.keys():
                        new_swift = SwiftAPI(port=port['device'])
                        new_swift.waiting_ready()
                        device_info = new_swift.get_device_info()
                        print(new_swift.port, device_info)
                        firmware_version = device_info['firmware_version']
                        if firmware_version and not firmware_version.startswith(('0.', '1.', '2.', '3.')):
                            new_swift.set_speed_factor(0.00001)
                        new_swift.set_mode(mode=0)
                        with lock:
                            pos = [150, 0, 150]
                            for swift in swifts.values():
                                swift.flush_cmd()
                            if len(swifts.values()) > 0:
                                time.sleep(1)
                            for swift in swifts.values():
                                pos = swift.get_position()
                                if isinstance(pos, list):
                                    # print('sync pos:', pos)
                                    break
                            # new_swift.reset(speed=speed)
                            swifts[port['device']] = new_swift

                            for swift in swifts.values():
                                swift.set_position(x=pos[0], y=pos[1], z=pos[2], speed=speed, wait=False)
                            for swift in swifts.values():
                                if swift.connected:
                                    swift.flush_cmd(wait_stop=True)
                            # if len(swifts) > 1:
                            #     time.sleep(3)
                    else:
                        swift = swifts[port['device']]
                        if not swift.connected:
                            with lock:
                                swifts.pop(port['device'])
            except Exception as e:
                pass
            time.sleep(0.001)


listen = ListenPort()
listen.start()


def multi_swift_cmd(cmd, *args, **kwargs):
    wait = kwargs.pop('wait', False)
    timeout = kwargs.get('timeout', None)
    with lock:
        for swift in swifts.values():
            if swift.connected:
                swift_cmd = getattr(swift, cmd)
                swift_cmd(*args, wait=False, **kwargs)
        if wait:
            for swift in swifts.values():
                if swift.connected:
                    swift.flush_cmd(timeout)
    time.sleep(0.001)


while True:
    multi_swift_cmd('set_position', x=300, y=0, z=150, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi_swift_cmd('set_position', x=200, y=100, z=100, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi_swift_cmd('set_position', x=200, y=-100, z=100, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)

    multi_swift_cmd('set_position', x=200, y=0, z=150, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=50, speed=speed, wait=True, timeout=timeout)
    multi_swift_cmd('set_position', z=150, speed=speed, wait=True, timeout=timeout)
    # time.sleep(0.01)





