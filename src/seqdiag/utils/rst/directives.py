# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from docutils.parsers import rst
from seqdiag.utils.rst.nodes import seqdiag as seqdiag_node
from blockdiag.utils.rst import directives


directive_options_default = dict(format='PNG',
                                 antialias=False,
                                 fontpath=None,
                                 outputdir=None,
                                 nodoctype=False,
                                 noviewbox=False,
                                 inline_svg=False)
directive_options = {}


class SeqdiagDirective(directives.BlockdiagDirective):
    name = "seqdiag"
    node_class = seqdiag_node

    @property
    def global_options(self):
        return directive_options


def setup(**kwargs):
    for key, value in directive_options_default.items():
        directive_options[key] = kwargs.get(key, value)

    rst.directives.register_directive("seqdiag", SeqdiagDirective)
