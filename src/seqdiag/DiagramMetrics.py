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
from blockdiag.utils import Box, XY
from blockdiag.utils.collections import namedtuple

try:
    from blockdiag.utils.PILTextFolder import PILTextFolder as TextFolder
except ImportError:
    from blockdiag.utils.TextFolder import TextFolder


class DiagramMetrics(blockdiag.DiagramMetrics.DiagramMetrics):
    edge_height = 10

    def __init__(self, diagram, **kwargs):
        super(DiagramMetrics, self).__init__(diagram, **kwargs)

        self.node_count = len(diagram.nodes)
        self.edges = diagram.edges
        self.separators = diagram.separators
        self.page_padding = [0, 0, self.cellsize * 3, 0]

        if diagram.edge_length:
            span_width = diagram.edge_length - self.node_width
            if span_width < 0:
                msg = "WARNING: edge_length is too short: %d\n" % \
                      diagram.edge_length
                sys.stderr.write(msg)

                span_width = 0

            self.span_width = span_width

        for edge in diagram.edges:
            edge.textwidth, edge.textheight = self.edge_textsize(edge)

            height = self.edge_height + edge.textheight
            if edge.diagonal:
                height += self.node_height * 3 / 4
            elif edge.direction == 'self':
                height += self.cellsize * 2

            if edge.leftnote:
                edge.leftnotesize = self.edge_leftnotesize(edge)
                if height < edge.leftnotesize.y:
                    height = edge.leftnotesize.y

            if edge.rightnote:
                edge.rightnotesize = self.edge_rightnotesize(edge)
                if height < edge.rightnotesize.y:
                    height = edge.rightnotesize.y

            self.spreadsheet.set_node_height(edge.order + 1, height)

    def pagesize(self, width=None, height=None):
        width = self.node_count
        height = len(self.edges) + len(self.separators) + 1
        return super(DiagramMetrics, self).pagesize(width, height)

    @property
    def bottomheight(self):
        height = len(self.edges) + len(self.separators)
        dummy = elements.DiagramNode(None)
        dummy.xy = XY(1, height)
        x, y = self.spreadsheet._node_bottomright(dummy, use_padding=False)
        return y

    @property
    def edge_length(self):
        return self.node_width + self.span_width

    def lifeline(self, node):
        delayed = []
        for sep in self.separators:
            if sep.type == 'delay':
                delayed.append(sep)

        lines = []
        d = self.cellsize
        pt = self.node(node).bottom
        for sep in delayed:
            m = self.cell(sep)
            y1 = m.top.y
            y2 = m.bottom.y
            lines.append(((pt, XY(pt.x, y1)), '8,4'))
            lines.append(((XY(pt.x, y1 + d), XY(pt.x, y2 - d)), '2,8'))

            pt = XY(pt.x, y2)

        y = self.bottomheight + self.cellsize * 4
        lines.append(((pt, XY(pt.x, y)), '8,4'))

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
            y2 = self.bottomheight + self.cellsize * 2

        index = activity['level']
        base_x = self.cell(node).bottom.x
        box = (base_x + (index - 1) * self.cellsize / 2, y1,
               base_x + (index + 1) * self.cellsize / 2, y2)

        return box

    def activity_shadow(self, node, activity):
        box = self.activity_box(node, activity)

        return (box[0] + self.shadow_offset.x, box[1] + self.shadow_offset.y,
                box[2] + self.shadow_offset.x, box[3] + self.shadow_offset.y)

    def edge_textsize(self, edge):
        width = 0
        height = 0
        if edge.label:
            if edge.direction == 'self':
                cell = self.cell(edge.left_node)
                width = (cell.right.x - cell.left.x) / 2 + self.span_width / 2
            else:
                width = self.cell(edge.right_node).center.x - \
                        self.cell(edge.left_node).center.x
            width, height = self.textsize(edge.label, width,
                                          fontsize=edge.fontsize)

        return XY(width, height)

    def edge_leftnotesize(self, edge):
        width = 0
        height = 0
        if edge.leftnote:
            cell = self.cell(edge.left_node)
            width = cell.center.x - self.cellsize * 3
            width, height = self.textsize(edge.leftnote, width,
                                          fontsize=edge.fontsize)

        return XY(width, height)

    def edge_rightnotesize(self, edge):
        width = 0
        height = 0
        if edge.rightnote:
            cell = self.cell(edge.right_node)
            if edge.direction == 'self':
                width = self.pagesize().x - cell.right.x - self.cellsize * 3
            else:
                width = self.pagesize().x - cell.center.x - self.cellsize * 6
            width, height = self.textsize(edge.rightnote, width,
                                          fontsize=edge.fontsize)

        return XY(width, height)

    def cell(self, obj, use_padding=True):
        if isinstance(obj, (elements.DiagramEdge, elements.EdgeSeparator)):
            klass = namedtuple('_', 'xy width height colwidth colheight')
            edge = klass(XY(1, obj.order + 1), None, None, 1, 1)
            return super(DiagramMetrics, self).cell(edge, use_padding=False)
        else:
            return super(DiagramMetrics, self).cell(obj, use_padding)

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
        cell = self.metrics.cell(self.edge)
        if cell.height == self.edge.leftnotesize.y or \
           cell.height == self.edge.rightnotesize.y:
            return cell.center.y
        else:
            return cell.top.y + self.edge.textheight

    @property
    def shaft(self):
        m = self.metrics
        baseheight = self.baseheight

        if self.edge.direction == 'self':
            node = self.edge.node1
            fold_width = m.spreadsheet.node_width[node.xy.x] / 2 + \
                         m.spreadsheet.span_width[node.xy.x + 1] / 2
            fold_height = m.cellsize * 2

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
                height = m.node_height * 3 / 4
                if self.edge.direction == 'right':
                    line = [XY(x1 + margin, baseheight),
                            XY(x2 - margin, baseheight + height)]
                else:
                    line = [XY(x1 + margin, baseheight + height),
                            XY(x2 - margin, baseheight)]
            else:
                line = [XY(x1 + margin, baseheight),
                        XY(x2 - margin, baseheight)]

            if self.edge.failed:
                edge_length = self.metrics.edge_length
                pt1, pt2 = line
                if self.edge.direction == 'right':
                    pt2 = XY(pt2.x - edge_length / 2, (pt1.y + pt2.y) / 2)
                else:
                    pt1 = XY(pt1.x + edge_length / 2, (pt1.y + pt2.y) / 2)
                line = [pt1, pt2]

        return line

    @property
    def failedmark(self):
        lines = []
        if self.edge.failed:
            r = self.metrics.cellsize
            if self.edge.direction == 'right':
                pt = self.shaft[-1]
                lines.append((XY(pt.x + r, pt.y - r),
                              XY(pt.x + r * 3, pt.y + r)))
                lines.append((XY(pt.x + r, pt.y + r),
                              XY(pt.x + r * 3, pt.y - r)))
            else:
                pt = self.shaft[0]
                lines.append((XY(pt.x - r * 3, pt.y - r),
                              XY(pt.x - r, pt.y + r)))
                lines.append((XY(pt.x - r * 3, pt.y + r),
                              XY(pt.x - r, pt.y - r)))

        return lines

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
            x = m.node(self.edge.node1).bottom.x + \
                self.activity_line_width(self.edge.node1)
        elif self.edge.direction == 'right':
            x = m.node(self.edge.left_node).bottom.x + \
                self.activity_line_width(self.edge.node1)
        else:  # left
            x = m.node(self.edge.right_node).bottom.x - self.edge.textwidth

        y1 = self.baseheight - self.edge.textheight
        return (x, y1, x + self.edge.textwidth, y1 + self.edge.textheight)

    def activity_line_width(self, node):
        m = self.metrics

        index = self.edge.order
        activities = [a for a in node.activities if index in a['lifetime']]
        if activities:
            level = max(a['level'] for a in activities)
        else:
            level = 0

        return m.cellsize / 2 * level

    @property
    def leftnotebox(self):
        if not self.edge.leftnote:
            return Box(0, 0, 0, 0)

        m = self.metrics
        cell = m.cell(self.edge.left_node)
        notesize = self.edge.leftnotesize

        x = cell.center.x - m.cellsize * 3 - notesize.x
        y = self.baseheight - notesize.y / 2
        return Box(x, y, x + notesize.x, y + notesize.y)

    @property
    def leftnoteshape(self):
        if not self.edge.leftnote:
            return []

        r = self.metrics.cellsize
        box = self.leftnotebox
        return [XY(box[0], box[1]), XY(box[2], box[1]),
                XY(box[2] + r, box[1] + r), XY(box[2] + r, box[3]),
                XY(box[0],  box[3]), XY(box[0], box[1])]

    @property
    def rightnotebox(self):
        if not self.edge.rightnote:
            return Box(0, 0, 0, 0)

        m = self.metrics
        cell = m.cell(self.edge.right_node)
        if self.edge.direction == 'self':
            x = cell.right.x + m.cellsize * 2
        else:
            x = cell.center.x + m.cellsize * 2

        notesize = self.edge.rightnotesize
        y = self.baseheight - notesize.y / 2
        return Box(x, y, x + notesize.x, y + notesize.y)

    @property
    def rightnoteshape(self):
        if not self.edge.rightnote:
            return []

        r = self.metrics.cellsize
        box = self.rightnotebox
        return [XY(box[0], box[1]), XY(box[2], box[1]),
                XY(box[2] + r, box[1] + r), XY(box[2] + r, box[3]),
                XY(box[0],  box[3]), XY(box[0], box[1])]


class SeparatorMetrics(object):
    def __init__(self, separator, metrics):
        self.metrics = metrics
        self.separator = separator

        x1, x2 = self.baseline
        y1 = self.baseheight
        y2 = y1 + self.metrics.node_height
        d = self.metrics.cellsize / 4

        lines = TextFolder((x1, y1, x2, y2), separator.label)
        box = lines.outlinebox
        self.labelbox = (box[0] - d, box[1] - d, box[2] + d, box[3] + d)

    @property
    def baseheight(self):
        return self.metrics.cell(self.separator).top.y

    @property
    def baseline(self):
        dummy = elements.DiagramNode(None)
        dummy.xy = XY(0, 1)
        dummy.colwidth = self.metrics.node_count
        m = self.metrics.cell(dummy)
        r = self.metrics.cellsize * 3
        return (m.x1 - r, m.x2 + r)

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
