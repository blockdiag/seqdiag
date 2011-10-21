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

import elements
import blockdiag.DiagramMetrics
from blockdiag.utils.XY import XY

try:
    from blockdiag.utils.PILTextFolder import PILTextFolder as TextFolder
except ImportError:
    from blockdiag.utils.TextFolder import TextFolder


class DiagramMetrics(blockdiag.DiagramMetrics.DiagramMetrics):
    def __init__(self, diagram, **kwargs):
        super(DiagramMetrics, self).__init__(diagram, **kwargs)

        self.node_count = len(diagram.nodes)
        self.edges = diagram.edges
        self.edge_height = self.node_height

        if diagram.edge_height:
            self.edge_height = diagram.edge_height

        if diagram.edge_length:
            span_width = diagram.edge_length - self.node_width
            if span_width < 0:
                msg = "WARNING: edge_length is too short: %d\n" % \
                      diagram.edge_length
                sys.stderr.write(msg)

                span_width = 0

            self.span_width = span_width

    @property
    def pagesize(self):
        size = super(DiagramMetrics, self).pagesize(self.node_count, 1)

        height = int(sum(e.height for e in self.edges) * self.edge_height)
        height += self.span_height + self.edge_height / 2

        return XY(size.x, size.y + height)

    def groupbox(self, group):
        box = list(self.cell(group).marginbox)
        box[3] = self.pagesize.y - self.page_margin.y - self.page_padding[2]

        return box

    def lifeline(self, node):
        delayed = []
        for e in self.edges:
             if isinstance(e, elements.EdgeSeparator) and e.type == 'delay':
                 delayed.append(e.y)

        lines = []
        d = self.cellsize
        pt = self.node(node).bottom
        for i in delayed:
             y1 = self.edge_baseheight + self.span_height + int(i * self.edge_height)
             y2 = y1 + self.edge_height
             lines.append(((pt, XY(pt.x, y1)), 'dashed'))
             lines.append(((XY(pt.x, y1 + d), XY(pt.x, y2 - d)), 'dotted'))

             pt = XY(pt.x, y2)

        y = self.pagesize.y - self.page_margin.y - self.page_padding[2]
        lines.append(((pt, XY(pt.x, y)), 'dashed'))

        return lines

    def activity_box(self, node, activity):
        # y coodinates for top of activity box
        starts = activity['lifetime'][0]
        edge = self.edges[starts]
        y1 = self.edge(edge).baseheight
        if edge.diagonal and edge.node2 == node:
            y1 += self.edge_height * 3 / 4

        # y coodinates for bottom of activity box
        ends = activity['lifetime'][-1] + 1
        if ends < len(self.edges):
            y2 = self.edge(self.edges[ends]).baseheight
        else:
            y2 = self.pagesize.y - self.page_margin.y - self.edge_height / 2

        index = activity['level']
        base_x = self.cell(node).bottom.x
        box = (base_x + (index - 1) * self.cellsize / 2, y1,
               base_x + (index + 1) * self.cellsize / 2, y2)

        return box

    def activity_shadow(self, node, activity):
        box = self.activity_box(node, activity)

        return (box[0] + self.shadow_offset.x, box[1] + self.shadow_offset.y,
                box[2] + self.shadow_offset.x, box[3] + self.shadow_offset.y)

    @property
    def edge_baseheight(self):
        return self.cell(self.edges[0].node1).bottom.y

    def edge(self, edge):
        return EdgeMetrics(edge, self)

    def separator(self, separator):
        return SeparatorMetrics(separator, self)


class EdgeMetrics(object):
    def __init__(self, edge, metrics):
        self.metrics = metrics
        self.edge = edge

    @property
    def baseheight(self):
        return self.metrics.edge_baseheight + \
               self.metrics.span_height + self.metrics.edge_height / 2 + \
               int(self.edge.y * self.metrics.edge_height)

    @property
    def shaft(self):
        m = self.metrics
        baseheight = self.baseheight

        if self.edge.direction == 'self':
            fold_width = m.node_width / 2 + m.cellsize
            fold_height = m.edge_height / 4

            # adjust textbox to right on activity-lines
            base_x = self.metrics.node(self.edge.node1).bottom.x
            x1 = base_x + self.activity_line_width(self.edge.node1)

            line = [XY(x1 + m.cellsize, baseheight),
                    XY(x1 + fold_width, baseheight),
                    XY(x1 + fold_width, baseheight + fold_height),
                    XY(x1 + m.cellsize, baseheight + fold_height)]
        else:
            x1 = self.metrics.node(self.edge.left_node).bottom.x + \
                 self.activity_line_width(self.edge.left_node)
            x2 = self.metrics.node(self.edge.right_node).bottom.x

            margin = m.cellsize
            if self.edge.diagonal:
                line = [XY(x1 + margin, baseheight),
                        XY(x2 - margin, baseheight + m.edge_height * 3 / 4)]
            else:
                line = [XY(x1 + margin, baseheight),
                        XY(x2 - margin, baseheight)]

        return line

    @property
    def head(self):
        cell = self.metrics.cellsize

        head = []
        if self.edge.direction == 'right':
            xy = self.shaft[-1]
            head.append(XY(xy.x - cell, xy.y - cell / 2))
            head.append(xy)
            head.append(XY(xy.x - cell, xy.y + cell / 2))
        elif self.edge.direction == 'left':
            xy = self.shaft[0]
            head.append(XY(xy.x + cell, xy.y - cell / 2))
            head.append(xy)
            head.append(XY(xy.x + cell, xy.y + cell / 2))
        else:  # self
            xy = self.shaft[-1]
            head.append(XY(xy.x + cell, xy.y - cell / 2))
            head.append(xy)
            head.append(XY(xy.x + cell, xy.y + cell / 2))

        return head

    @property
    def textbox(self):
        m = self.metrics

        if self.edge.direction == 'self':
            x1 = m.node(self.edge.node1).bottom.x
            x2 = x1 + m.node_width + m.span_width

            x = [x1, x2]
        else:
            x = [m.node(self.edge.node1).bottom.x,
                 m.node(self.edge.node2).bottom.x]
            x.sort()

        x[0] += self.activity_line_width(self.edge.node1)

        baseheight = self.baseheight - self.metrics.edge_height / 2
        return (x[0], baseheight,
                x[1], baseheight + int(m.edge_height * 0.45))

    def activity_line_width(self, node):
        m = self.metrics

        index = self.edge.y
        activities = [a for a in node.activities if index in a['lifetime']]
        if activities:
            level = max(a['level'] for a in activities)
        else:
            level = 0

        return m.cellsize / 2 * level


class SeparatorMetrics(object):
    def __init__(self, separator, metrics):
        self.metrics = metrics
        self.separator = separator

        x1, x2 = self.baseline
        y1 = self.baseheight
        y2 = y1 + self.metrics.edge_height
        d = self.metrics.cellsize / 4

        lines = TextFolder((x1, y1, x2, y2), separator.label,
                           adjustBaseline=True, font=self.metrics.font,
                           fontsize=self.metrics.fontsize)
        box = lines.outlineBox()
        self.labelbox = (box[0] - d, box[1] - d, box[2] + d, box[3] + d)

    @property
    def baseheight(self):
        return self.metrics.edge_baseheight + self.metrics.span_height + \
               int(self.separator.y * self.metrics.edge_height)

    @property
    def baseline(self):
        pagesize = self.metrics.pagesize
        padding = self.metrics.page_padding
        margin = self.metrics.page_margin
        return (margin.x + padding[3], pagesize.x - margin.x - padding[1])

    @property
    def lines(self):
        lines = []
        if self.separator.type == 'divider':
            y = (self.labelbox[1] + self.labelbox[3]) / 2
            x1, x2 = self.baseline
            d = self.metrics.cellsize / 4

            lines.append((XY(x1, y - d), XY(self.labelbox[0], y - d)))
            lines.append((XY(x1, y + d), XY(self.labelbox[0], y + d)))
            lines.append((XY(self.labelbox[2], y - d), XY(x2, y - d)))
            lines.append((XY(self.labelbox[2], y + d), XY(x2, y + d)))

        return lines
