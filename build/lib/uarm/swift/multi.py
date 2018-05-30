#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFactory, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import time


class MultiSwiftAPI(object):
    def __init__(self, swifts):
        self.swifts = swifts
        self.multi_cmd_sync('waiting_ready')

    def multi_reset(self, speed=10000):
        self.multi_cmd_sync('reset', speed=speed)
        time.sleep(2)

    def multi_cmd_sync(self, cmd, *args, **kwargs):
        kwargs.pop('wait', False)
        for swift in self.swifts:
            swift_cmd = getattr(swift, cmd)
            swift_cmd(*args, wait=False, **kwargs)
        self.multi_flush_cmd(kwargs.get('timeout', None))

    def multi_flush_cmd(self, timeout=None):
        for swift in self.swifts:
            swift.flush_cmd(timeout=timeout, wait_stop=True)
