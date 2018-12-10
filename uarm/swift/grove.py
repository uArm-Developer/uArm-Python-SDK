#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import functools
from . import protocol
from .utils import catch_exception
from .utils import REPORT_GROVE


class Grove(object):
    def __init__(self):
        pass

    @catch_exception
    def grove_init(self, pin=None, grove_type=None, value=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert pin is not None and grove_type is not None
        cmd = protocol.SET_GROVE_INIT.format(pin, grove_type)
        if not value:
            cmd += ' {}'.format(value)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def grove_control(self, pin=None, value=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert pin is not None and value is not None
        cmd = protocol.SET_GROVE_CONTROL.format(pin, value)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    def register_grove_callback(self, pin=None, callback=None):
        # assert pin is not None and grove_type is not None
        # return self._register_report_callback(REPORT_GROVE + '_{}_{}'.format(grove_type, pin), callback)
        assert pin is not None
        return self._register_report_callback(REPORT_GROVE + '_{}'.format(pin), callback)

    def release_grove_callback(self, pin=None, callback=None):
        return self._release_report_callback(REPORT_GROVE + '_{}'.format(pin), callback)

    @catch_exception
    def set_report_grove(self, pin=None, interval=0, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert isinstance(interval, (int, float)) and interval >= 0
        interval = str(round(interval * 1000, 2))
        cmd = protocol.SET_GROVE_REPORT.format(pin, interval)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))





