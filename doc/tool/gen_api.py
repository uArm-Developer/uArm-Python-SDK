#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import sys, os
import  pydoc

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from uf.wrapper.swift_api import SwiftAPI
from uf.wrapper.swift_with_ultrasonic import SwiftWithUltrasonic
from uf.wrapper.uarm_api import UarmAPI

from doc.tool.markdown_doc import MarkdownDoc

#open('../api/swift_api.md', 'w').write(pydoc.render_doc(SwiftAPI, renderer = pydoc.HTMLDoc()))

open('../api/swift_api.md', 'w').write(pydoc.render_doc(SwiftAPI, renderer = MarkdownDoc()))

open('../api/swift_with_ultrasonic.md', 'w').write(pydoc.render_doc(SwiftWithUltrasonic, renderer = MarkdownDoc()))

open('../api/uarm_api.md', 'w').write(pydoc.render_doc(UarmAPI, renderer = MarkdownDoc()))

print('done ...')

