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

import re
import sys
import blockdiag.elements
from blockdiag.elements import *
from blockdiag.utils.XY import XY


class DiagramNode(blockdiag.elements.DiagramNode):
    def __init__(self, id):
        super(DiagramNode, self).__init__(id)

        self.activity = []
        self.activities = []

    def activate(self, height, index):
        if len(self.activity) <= index:
            self.activity.insert(index, [])

        if len(self.activity[index]) > 0 and \
           self.activity[index][-1] != height - 1:
            self.deactivate(index)

        self.activity[index].append(height)

    def deactivate(self, index=None):
        if index is None:
            for i in range(len(self.activity)):
                self.deactivate(i)
            return

        if self.activity[index]:
            attr = {'lifetime': self.activity[index],
                    'level': index}
            self.activities.append(attr)

        self.activity[index] = []


class Diagram(blockdiag.elements.Diagram):
    def __init__(self):
        super(Diagram, self).__init__()

        self.int_attrs.append('edge_height')
        self.int_attrs.append('edge_length')

        self.draw_activation = True
        self.edge_height = None
        self.edge_length = None
        self.groups = []

    def set_draw_activation(self, value):
        if value == 'False':
            self.draw_activation = False
        else:
            self.draw_activation = True


class DiagramEdge(blockdiag.elements.DiagramEdge):
    def __init__(self, node1, node2):
        super(DiagramEdge, self).__init__(node1, node2)

        self.height = 1
        self.y = 0
        self.activate = True
        self.async = False
        self.diagonal = False
        self.return_label = ''

    @property
    def direction(self):
        if self.node1.xy.x == self.node2.xy.x:
            direction = 'self'
        elif self.node1.xy.x < self.node2.xy.x:
            # n1 .. n2
            if self.dir == 'forward':
                direction = 'right'
            else:
                direction = 'left'
        else:
            # n2 .. n1
            if self.dir == 'forward':
                direction = 'left'
            else:
                direction = 'right'

        return direction

    def set_diagonal(self, value):
        self.diagonal = True
        self.height = 1.5

    def set_async(self, value):
        self.dir = 'forward'

    def set_return(self, value):
        self.return_label = value

    def set_activate(self, value):
        self.activate = True

    def set_noactivate(self, value):
        self.activate = False

    def set_dir(self, value):
        dir = value.lower()
        if dir in ('back', 'both', 'forward'):
            self.dir = dir
        elif dir == '=>':
            self.dir = 'both'
        elif dir in ('->', '->>', '-->', '-->>'):
            self.dir = 'forward'

            if re.search('--', dir):
                self.style = 'dashed'
            else:
                self.style = None

            if re.search('>>', dir):
                self.async = True
            else:
                self.async = False
        elif dir in ('<-', '<<-', '<--', '<<--'):
            self.dir = 'back'

            if re.search('--', dir):
                self.style = 'dashed'
            else:
                self.style = None

            if re.search('<<', dir):
                self.async = True
            else:
                self.async = False
        else:
            msg = "WARNING: unknown edge dir: %s\n" % dir
            sys.stderr.write(msg)
