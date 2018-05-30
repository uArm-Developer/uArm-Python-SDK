# !/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import functools
from ..utils.log import logger

REPORT_POWER_ID = 'POWER'
REPORT_POSITION_ID = 'POSITION'
REPORT_KEY0_ID = 'KEY0'
REPORT_KEY1_ID = 'KEY1'
REPORT_LIMIT_SWITCH_ID = 'LIMIT_SWITCH'
REPORT_GROVE = 'GROVE'


def catch_exception(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        try:
            if args[0].blocked:
                return 'uArm is blocked, please waiting or restart'
            if args[0].connected:
                return func(*args, **kwargs)
            else:
                logger.error('uArm is not connect')
                return 'uArm is not connect'
        except Exception as e:
            logger.error('{} - {} - {}'.format(type(e).__name__, func.__name__, e))
    return decorator
