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
    def set_gripper(self, catch=False, timeout=None, wait=True, callback=None):
        def _handle(ret, callback=None):
            if ret != protocol.TIMEOUT:
                ret = ret[0]
            if callable(callback):
                callback(ret)
            else:
                return ret

        assert isinstance(catch, bool) or (isinstance(catch, int) and catch >= 0)
        cmd = protocol.SET_GRIPPER.format(1 if catch else 0)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            start = time.time()
            timeout = timeout if isinstance(timeout, (int, float)) and timeout > 0 else self.cmd_timeout
            while time.time() - start < timeout:
                catch = self.get_gripper_catch()
                if isinstance(catch, int) and (catch == 2 or catch == 0):
                    break
                time.sleep(0.3)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, callback=callback))

    @catch_exception
    def get_gripper_catch(self, wait=True, timeout=None, callback=None):
        def _handle(ret, callback=None):
            if ret[0] == protocol.OK:
                ret = int(ret[1][1])
            if callable(callback):
                callback(ret)
            else:
                return ret

        cmd = protocol.GET_GRIPPER
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, callback=callback))

