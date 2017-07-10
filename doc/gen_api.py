#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import sys, os
import  pydoc

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from uf.wrapper.swift_api import SwiftAPI
from doc.markdown_doc import MarkdownDoc

#open('swift_api.md', 'w').write(pydoc.render_doc(SwiftAPI, renderer = pydoc.HTMLDoc()))
open('swift_api.md', 'w').write(pydoc.render_doc(SwiftAPI, renderer = MarkdownDoc()))
print('done ...')

