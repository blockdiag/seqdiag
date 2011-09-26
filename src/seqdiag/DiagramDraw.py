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

import sys
import blockdiag.DiagramDraw
from blockdiag.utils.XY import XY


class DiagramDraw(blockdiag.DiagramDraw.DiagramDraw):
    def pagesize(self, scaled=False):
        if scaled:
            m = self.metrix
        else:
            m = self.metrix.originalMetrix()

        return m.pageSize(self.nodes)

    def draw(self, **kwargs):
        super(DiagramDraw, self).draw(**kwargs)

        for group in self.diagram.groups:
            self.group_label(group, **kwargs)

    def _draw_background(self):
        m = self.metrix.originalMetrix()
        pagesize = self.pagesize()

        for group in self.diagram.groups:
            box = m.groupBox(group)
            self.drawer.rectangle(box, fill=group.color, filter='blur')

        for node in self.nodes:
            node.activities.sort(lambda x, y: cmp(x['level'], y['level']))

        for node in self.nodes:
            for activity in node.activities:
                self.node_activity_shadow(node, activity)

        super(DiagramDraw, self)._draw_background()

        for node in self.nodes:
            self.lifelines(node)

            for activity in node.activities:
                self.node_activity(node, activity)

    def node_activity_shadow(self, node, activity):
        box = self.metrix.originalMetrix().activity_shadow(node, activity)
        self.drawer.rectangle(box, fill=self.shadow, filter='transp-blur')

    def node_activity(self, node, activity):
        box = self.metrix.originalMetrix().activity_box(node, activity)
        self.drawer.rectangle(box, width=1, outline=self.diagram.linecolor,
                              fill='moccasin')

    def lifelines(self, node):
        line = self.metrix.originalMetrix().lifeline(node)
        self.drawer.line(line, fill=self.diagram.linecolor, style='dotted')

    def _prepare_edges(self):
        pass

    def edge(self, edge):
        # render shaft of edges
        m = self.metrix.edge(edge)
        shaft = m.shaft
        self.drawer.line(shaft, fill=edge.color, style=edge.style)

        # render head of edges
        head = m.head
        if edge.async:
            self.drawer.line((head[0], head[1]), fill=color)
            self.drawer.line((head[1], head[2]), fill=color)
        else:
            self.drawer.polygon(head, outline=edge.color, fill=edge.color)

    def edge_label(self, edge):
        if edge.direction in ('right', 'self'):
            halign = 'left'
        else:
            halign = 'right'

        textbox = self.metrix.edge(edge).textbox
        self.drawer.textarea(textbox, edge.label,
                             fill=edge.color, halign=halign,
                             font=self.font, fontsize=self.metrix.fontSize)


from DiagramMetrix import DiagramMetrix
DiagramDraw.set_metrix_class(DiagramMetrix)
