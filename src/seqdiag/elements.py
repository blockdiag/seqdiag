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

import blockdiag.elements
from blockdiag.utils import XY, Size, images
from blockdiag.utils.logging import warning


class NodeGroup(blockdiag.elements.NodeGroup):
    pass


class DiagramNode(blockdiag.elements.DiagramNode):
    def __init__(self, _id):
        super(DiagramNode, self).__init__(_id)

        self.activated = False
        self.activity = []
        self.activities = []

    def set_activated(self, value):
        self.activated = True

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

    def __init__(self, _type, label, href):
        super(EdgeSeparator, self).__init__()
        self.label = label
        self.href = href
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

    # name -> (dir, style, asynchronous)
    ARROW_DEF = {
        'both': ('both', None, False),
        '=>': ('both', None, False),
        'forward': ('forward', None, False),
        '->': ('forward', None, False),
        '-->': ('forward', 'dashed', False),
        '->>': ('forward', None, True),
        '-->>': ('forward', 'dashed', True),
        'back': ('back', None, False),
        '<-': ('back', None, False),
        '<--': ('back', 'dashed', False),
        '<<-': ('back', None, True),
        '<<--': ('back', 'dashed', True)
    }

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
        self.asynchronous = False
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
        params = self.ARROW_DEF.get(value.lower())
        if params is None:
            warning("unknown edge dir: %s", value)
        else:
            self.dir, self.style, self.asynchronous = params

            if self.node1 == self.node2 and self.dir in ('forward', 'back'):
                self.activate = False

    def to_desctable(self):
        params = (self.dir, self.style, self.asynchronous)
        for arrow_type, settings in self.ARROW_DEF.items():
            if params == settings and not arrow_type.isalpha():
                label = "%s %s %s" % (self.node1.label,
                                      arrow_type,
                                      self.node2.label)
                return [label, self.description]


class AltBlock(blockdiag.elements.Base):
    basecolor = (0, 0, 0)
    linecolor = (0, 0, 0)
    width = None
    height = None

    @classmethod
    def clear(cls):
        super(EdgeSeparator, cls).clear()
        cls.basecolor = (0, 0, 0)
        cls.linecolor = (0, 0, 0)

    @classmethod
    def set_default_linecolor(cls, color):
        color = images.color_to_rgb(color)
        cls.linecolor = color

    def __init__(self, _type, _id):
        self.type = _type
        self.id = _id
        self.xlevel = 1
        self.ylevel_top = 1
        self.ylevel_bottom = 1
        self.edges = []
        self.color = self.basecolor

    @property
    def xy(self):
        if len(self.edges) == 0:
            return XY(0, 0)
        else:
            x = min(e.left_node.xy.x for e in self.edges)
            y = min(e.order for e in self.edges) + 1
            return XY(x, y)

    @property
    def colwidth(self):
        if len(self.edges) == 0:
            return 1
        else:
            x2 = max(e.right_node.xy.x for e in self.edges)
            return x2 - self.xy.x + 1

    @property
    def colheight(self):
        if len(self.edges) == 0:
            return 1
        else:
            y2 = max(e.order for e in self.edges) + 1
            return y2 - self.xy.y + 1


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
        self.altblocks = []

    def traverse_groups(self, preorder=False):
        return self.groups

    def set_default_textcolor(self, color):
        super(Diagram, self).set_default_textcolor(color)

        EdgeSeparator.set_default_text_color(color)

    def set_default_linecolor(self, color):
        super(Diagram, self).set_default_linecolor(color)

        color = images.color_to_rgb(color)
        AltBlock.set_default_linecolor(color)

    def set_default_note_color(self, color):
        color = images.color_to_rgb(color)
        self._DiagramEdge.set_default_note_color(color)

    def set_default_fontfamily(self, fontfamily):
        super(Diagram, self).set_default_fontfamily(fontfamily)
        EdgeSeparator.set_default_fontfamily(fontfamily)

    def set_default_fontsize(self, fontsize):
        super(Diagram, self).set_default_fontsize(fontsize)
        EdgeSeparator.set_default_fontsize(fontsize)

    def set_activation(self, value):
        value = value.lower()
        if value == 'none':
            self.activation = value
        else:
            warning("unknown activation style: %s", value)

    def set_autonumber(self, value):
        if value.lower() == 'false':
            self.autonumber = False
        else:
            self.autonumber = True

    def set_edge_height(self, value):
        warning("edge_height is obsoleted; use span_height")
        self.span_height = int(value)
