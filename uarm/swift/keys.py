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
from .utils import REPORT_KEY0_ID, REPORT_KEY1_ID


class Keys(object):
    def __init__(self):
        pass

    def register_key0_callback(self, callback=None):
        return self._register_report_callback(REPORT_KEY0_ID, callback)

    def release_key0_callback(self, callback=None):
        return self._release_report_callback(REPORT_KEY0_ID, callback)

    def register_key1_callback(self, callback=None):
        return self._register_report_callback(REPORT_KEY1_ID, callback)

    def release_key1_callback(self, callback=None):
        return self._release_report_callback(REPORT_KEY1_ID, callback)

    @catch_exception
    def set_report_keys(self, on=True, wait=True, timeout=None, callback=None, **kwargs):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        is_on = kwargs.get('is_on', None)
        on = is_on if is_on is not None else on
        assert isinstance(on, bool) or (isinstance(on, int) and on >= 0)
        cmd = protocol.SET_REPORT_KEYS.format(int(not on))
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))
