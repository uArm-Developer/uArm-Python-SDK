#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import sys, os
import pydoc

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from uarm.wrapper import SwiftAPI

from doc.tool.markdown_doc import MarkdownDoc

open('../api/swift_api.md', 'w', encoding='utf-8').write(pydoc.render_doc(SwiftAPI, renderer=MarkdownDoc()))

print('done ...')

