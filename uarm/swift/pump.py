#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import time
import functools
from . import protocol
from .utils import catch_exception
from .utils import REPORT_LIMIT_SWITCH_ID


class Pump(object):
    def __init__(self):
        pass

    def register_limit_switch_callback(self, callback=None):
        return self._register_report_callback(REPORT_LIMIT_SWITCH_ID, callback)

    def release_limit_switch_callback(self, callback=None):
        return self._release_report_callback(REPORT_LIMIT_SWITCH_ID, callback)

    @catch_exception
    def set_pump(self, on=False, timeout=None, wait=True, check=False, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert isinstance(on, bool) or (isinstance(on, int) and on >= 0)
        cmd = protocol.SET_PUMP.format(1 if on else 0)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            if check:
                start = time.time()
                timeout = timeout if isinstance(timeout, (int, float)) and timeout > 0 else self.cmd_timeout
                while time.time() - start < timeout:
                    grabbed = self.get_pump_status()
                    if isinstance(grabbed, int) and (grabbed == 2 or grabbed == 0):
                        break
                    time.sleep(0.3)
            return _handle(ret)
            # ret = self.send_cmd_sync(cmd, timeout=timeout)
            # return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_limit_switch(self, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = bool(int(_ret[1][1]))
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        cmd = protocol.GET_LIMIT_SWITCH
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_pump_status(self, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = int(_ret[1][1])
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        cmd = protocol.GET_PUMP
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

