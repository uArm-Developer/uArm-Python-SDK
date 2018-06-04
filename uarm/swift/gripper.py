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


class Gripper(object):
    def __init__(self):
        pass

    @catch_exception
    def set_gripper(self, catch=False, timeout=None, wait=True, check=False, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert isinstance(catch, bool) or (isinstance(catch, int) and catch >= 0)
        cmd = protocol.SET_GRIPPER.format(1 if catch else 0)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            if check:
                start = time.time()
                timeout = timeout if isinstance(timeout, (int, float)) and timeout > 0 else self.cmd_timeout
                while time.time() - start < timeout:
                    catch = self.get_gripper_catch()
                    if isinstance(catch, int) and (catch == 2 or catch == 0):
                        break
                    time.sleep(0.3)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_gripper_catch(self, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = int(_ret[1][1])
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        cmd = protocol.GET_GRIPPER
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

