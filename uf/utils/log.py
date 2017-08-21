#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from datetime import datetime
import logging
logging.VERBOSE = 5


def logger_init(level=logging.INFO, filename=None):
    if filename is None:
        filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'
    logging.addLevelName(logging.VERBOSE, 'VERBOSE')
    logging.basicConfig(filename=filename, format='%(asctime)s %(levelname)s: %(name)s: %(message)s', level=level)
