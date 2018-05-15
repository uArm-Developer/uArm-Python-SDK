#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import functools
from . import protocol

REPORT_GROVE = 'GROVE'


class Grove(object):
    def __init__(self):
        pass

    def grove_init(self, pin=None, grove_type=None, value=None, wait=True, timeout=None, callback=None):
        def _handle(ret, callback=None):
            if ret[0] == protocol.OK:
                ret = ret[0]
            if callable(callback):
                callback(ret)
            else:
                return ret

        assert pin is not None and grove_type is not None
        cmd = protocol.SET_GROVE_INIT.format(pin, grove_type)
        if not value:
            cmd += ' {}'.format(value)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, callback=callback))

    def grove_control(self, pin=None, value=None, wait=True, timeout=None, callback=None):
        def _handle(ret, callback=None):
            if ret[0] == protocol.OK:
                ret = ret[0]
            if callable(callback):
                callback(ret)
            else:
                return ret

        assert pin is not None and value is not None
        cmd = protocol.SET_GROVE_CONTROL.format(pin, value)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, callback=callback))

    def register_grove_callback(self, pin=None, grove_type=None, callback=None):
        assert pin is not None and grove_type is not None
        return self._register_report_callback(REPORT_GROVE + '_{}_{}'.format(grove_type, pin), callback)

    def set_report_grove(self, pin=None, interval=0.5):
        assert isinstance(interval, (int, float)) and interval >= 0
        cmd = protocol.SET_GROVE_REPORT.format(pin, interval)
        return self.send_cmd_sync(cmd)



