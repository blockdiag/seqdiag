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
from blockdiag.utils import images, Size


class DiagramNode(blockdiag.elements.DiagramNode):
    def __init__(self, id):
        super(DiagramNode, self).__init__(id)

        self.activity = []
        self.activities = []

    def activate(self, height, index):
        if len(self.activity) <= index:
            self.activity.insert(index, [])

        if (len(self.activity[index]) > 0 and
           (self.activity[index][-1] != height - 1)):
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


class EdgeSeparator(blockdiag.elements.Base):
    basecolor = (208, 208, 208)
    linecolor = (0, 0, 0)

    @classmethod
    def clear(cls):
        super(EdgeSeparator, cls).clear()
        cls.basecolor = (208, 208, 208)
        cls.linecolor = (0, 0, 0)

    def __init__(self, _type, label):
        super(EdgeSeparator, self).__init__()
        self.label = label
        self.group = None
        self.style = None
        self.color = self.basecolor
        self.order = 0

        if _type == '===':
            self.type = 'divider'
        elif _type == '...':
            self.type = 'delay'


class DiagramEdge(blockdiag.elements.DiagramEdge):
    notecolor = (255, 182, 193)  # LightPink

    @classmethod
    def clear(cls):
        super(DiagramEdge, cls).clear()
        cls.notecolor = (255, 182, 193)

    @classmethod
    def set_default_note_color(cls, color):
        color = images.color_to_rgb(color)
        cls.notecolor = color

    def __init__(self, node1, node2):
        super(DiagramEdge, self).__init__(node1, node2)

        self.leftnote = None
        self.leftnotesize = Size(0, 0)
        self.rightnote = None
        self.rightnotesize = Size(0, 0)
        self.textwidth = 0
        self.textheight = 0
        self.order = 0
        self.activate = True
        self.async = False
        self.diagonal = False
        self.failed = False
        self.return_label = ''

    @property
    def left_node(self):
        if self.node1.xy.x <= self.node2.xy.x:
            return self.node1
        else:
            return self.node2

    @property
    def right_node(self):
        if self.node1.xy.x > self.node2.xy.x:
            return self.node1
        else:
            return self.node2

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

    def set_note(self, value):
        self.rightnote = value

    def set_diagonal(self, value):
        self.diagonal = True

    def set_async(self, value):
        self.dir = 'forward'

    def set_return(self, value):
        self.return_label = value

    def set_failed(self, value):
        self.failed = True
        self.activate = False

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


class Diagram(blockdiag.elements.Diagram):
    _DiagramNode = DiagramNode
    _DiagramEdge = DiagramEdge

    def __init__(self):
        super(Diagram, self).__init__()

        self.int_attrs.append('edge_length')

        self.activation = True
        self.autonumber = False
        self.edge_length = None
        self.groups = []
        self.separators = []

    def traverse_groups(self, preorder=False):
        return self.groups

    def set_default_note_color(self, color):
        color = images.color_to_rgb(color)
        self._DiagramEdge.set_default_note_color(color)

    def set_activation(self, value):
        value = value.lower()
        if value == 'none':
            self.activation = value
        else:
            msg = "WARNING: unknown activation style: %s\n" % value
            sys.stderr.write(msg)

    def set_autonumber(self, value):
        if value.lower() == 'false':
            self.autonumber = False
        else:
            self.autonumber = True

    def set_edge_height(self, value):
        msg = "WARNING: edge_height is obsoleted; use span_height\n"
        sys.stderr.write(msg)

        self.span_height = int(value)
