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

import blockdiag.drawer
from metrics import DiagramMetrics
from blockdiag.utils import XY


class DiagramDraw(blockdiag.drawer.DiagramDraw):
    MetricsClass = DiagramMetrics

    def _draw_background(self):
        for node in self.nodes:
            node.activities.sort(lambda x, y: cmp(x['level'], y['level']))

        if self.diagram.shadow_style != 'none':
            for node in self.nodes:
                for activity in node.activities:
                    self.node_activity_shadow(node, activity)

        if self.diagram.shadow_style != 'none':
            for edge in self.edges:
                self.edge_shadow(edge)

        super(DiagramDraw, self)._draw_background()

    def _draw_elements(self, **kwargs):
        for node in self.nodes:
            self.lifelines(node)

        super(DiagramDraw, self)._draw_elements(**kwargs)

        for sep in self.diagram.separators:
            self.separator(sep)

        for group in self.diagram.groups:
            self.group_label(group, **kwargs)

    def node_activity_shadow(self, node, activity):
        box = self.metrics.activity_shadow(node, activity)
        if self.diagram.shadow_style == 'solid':
            self.drawer.rectangle(box, fill=self.shadow)
        else:
            self.drawer.rectangle(box, fill=self.shadow, filter='transp-blur')

    def node_activity(self, node, activity):
        box = self.metrics.activity_box(node, activity)
        self.drawer.rectangle(box, width=1, outline=self.diagram.linecolor,
                              fill='moccasin')

    def lifelines(self, node):
        for line, style in self.metrics.lifeline(node):
            self.drawer.line(line, fill=self.diagram.linecolor, style=style)

        for activity in node.activities:
            self.node_activity(node, activity)

    def edge_shadow(self, edge):
        m = self.metrics
        dx, dy = m.shadow_offset

        if edge.leftnote:
            polygon = m.edge(edge).leftnoteshape
            shadow = [XY(pt.x + dx, pt.y + dy) for pt in polygon]
            if self.diagram.shadow_style == 'solid':
                self.drawer.polygon(shadow, fill=self.shadow,
                                    outline=self.shadow)
            else:
                self.drawer.polygon(shadow, fill=self.shadow,
                                    outline=self.shadow, filter='transp-blur')

        if edge.rightnote:
            polygon = m.edge(edge).rightnoteshape
            shadow = [XY(pt.x + dx, pt.y + dy) for pt in polygon]
            if self.diagram.shadow_style == 'solid':
                self.drawer.polygon(shadow, fill=self.shadow,
                                    outline=self.shadow)
            else:
                self.drawer.polygon(shadow, fill=self.shadow,
                                    outline=self.shadow, filter='transp-blur')

    def edge(self, edge):
        # render shaft of edges
        m = self.metrics.edge(edge)
        shaft = m.shaft
        self.drawer.line(shaft, fill=edge.color, style=edge.style)

        # render head of edges
        head = m.head
        if edge.async:
            self.drawer.line((head[0], head[1]), fill=edge.color)
            self.drawer.line((head[1], head[2]), fill=edge.color)
        else:
            self.drawer.polygon(head, outline=edge.color, fill=edge.color)

        if edge.failed:
            for line in m.failedmark:
                self.drawer.line(line, fill=edge.color)

        if edge.leftnote:
            polygon = m.leftnoteshape
            self.drawer.polygon(polygon, fill=edge.notecolor,
                                outline=self.fill)

            folded = [polygon[1], XY(polygon[1].x, polygon[2].y), polygon[2]]
            self.drawer.line(folded, fill=self.fill)

            self.drawer.textarea(m.leftnotebox, edge.leftnote,
                                 self.metrics.font_for(edge), fill=edge.color,
                                 valign='top', halign='left')

        if edge.rightnote:
            polygon = m.rightnoteshape
            self.drawer.polygon(polygon, fill=edge.notecolor,
                                outline=self.fill)

            folded = [polygon[1], XY(polygon[1].x, polygon[2].y), polygon[2]]
            self.drawer.line(folded, fill=self.fill)

            self.drawer.textarea(m.rightnotebox, edge.rightnote,
                                 self.metrics.font_for(edge), fill=edge.color,
                                 valign='top', halign='left')

    def edge_label(self, edge):
        m = self.metrics.edge(edge)

        if edge.label:
            if edge.direction in ('right', 'self'):
                halign = 'left'
            else:
                halign = 'right'

            self.drawer.textarea(m.textbox, edge.label,
                                 self.metrics.font_for(edge), fill=edge.color,
                                 halign=halign, valign='top')

    def separator(self, sep):
        m = self.metrics.separator(sep)
        for line in m.lines:
            self.drawer.line(line, fill=self.fill, style=sep.style)

        if sep.type == 'delay':
            self.drawer.rectangle(m.labelbox, fill='white', outline='white')
        elif sep.type == 'divider':
            self.drawer.rectangle(m.labelbox, fill=sep.color,
                                  outline=sep.linecolor)

        self.drawer.textarea(m.labelbox, sep.label,
                             self.metrics.font_for(sep), fill=sep.textcolor)
