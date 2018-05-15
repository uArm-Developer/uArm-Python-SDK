#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import functools
from . import protocol

REPORT_LIMIT_SWITCH_ID = 'LIMIT_SWITCH'


class Pump(object):
    def __init__(self):
        pass

    def register_limit_switch_callback(self, callback=None):
        return self._register_report_callback(REPORT_LIMIT_SWITCH_ID, callback)

    def set_pump(self, on=False, timeout=None, wait=True, callback=None):
        def _handle(ret, callback=None):
            if ret[0] == protocol.OK:
                ret = ret[0]
            if callable(callback):
                callback(ret)
            else:
                return ret

        assert isinstance(on, bool) or (isinstance(on, int) and on >= 0)
        cmd = protocol.SET_PUMP.format(1 if on else 0)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, callback=callback))

    def get_limit_switch(self, wait=True, timeout=None, callback=None):
        def _handle(ret, callback=None):
            if ret[0] == protocol.OK:
                ret = bool(int(ret[1][1]))
            if callable(callback):
                callback(ret)
            else:
                return ret

        cmd = protocol.GET_LIMIT_SWITCH
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, callback=callback))


