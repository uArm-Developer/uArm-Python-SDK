#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from .ufc_thread import UFCThread
from .ufc import UFC

def ufc_init(medium = 'thread'):
    if medium == 'thread':
        return UFCThread()
    else:
        raise Exception('medium not support')


