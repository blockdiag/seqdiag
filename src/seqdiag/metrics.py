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
from seqdiag import elements
import blockdiag.metrics
from blockdiag.utils import Box, XY
from blockdiag.utils.collections import namedtuple, defaultdict


class DiagramMetrics(blockdiag.metrics.DiagramMetrics):
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

            self.spreadsheet.set_span_width(0, self.span_width)
            self.spreadsheet.set_span_width(self.node_count, self.span_width)
            self.span_width = span_width

        for edge in diagram.edges:
            edge.textwidth, edge.textheight = self.edge_textsize(edge)

            height = self.edge_height + edge.textheight
            if edge.diagonal:
                height += self.node_height * 3 / 4
            elif edge.direction == 'self':
                height += self.cellsize * 2

            font = self.font_for(edge)
            if edge.leftnote:
                edge.leftnotesize = self.textsize(edge.leftnote, font=font)
                if height < edge.leftnotesize.height:
                    height = edge.leftnotesize.height

            if edge.rightnote:
                edge.rightnotesize = self.textsize(edge.rightnote, font=font)
                if height < edge.rightnotesize.height:
                    height = edge.rightnotesize.height

            self.spreadsheet.set_node_height(edge.order + 1, height)
            self.expand_pagesize_for_note(edge)

        span_width = defaultdict(int)
        span_height = defaultdict(int)
        for block in diagram.altblocks:
            x1, y1 = block.xy
            x2 = x1 + block.colwidth
            y2 = y1 + block.colheight

            for y in range(y1, y2):
                span_width[(x1, y)] += 1
                span_width[(x2, y)] += 1

            for x in range(x1, x2):
                if block.type != 'else':
                    span_height[(x, y1)] += 1
                span_height[(x, y2)] += 1

        for x in range(self.node_count + 1):
            widths = [span_width[xy] for xy in span_width if xy[0] == x]
            if widths:
                width = self.span_width + max(widths) * self.cellsize
                self.spreadsheet.set_span_width(x, width)

        for y in range(0, len(self.edges) + 1):
            blocks = [b for b in diagram.altblocks if b.edges[0].order == y]
            span_height = self.spreadsheet.span_height[y]
            span_height = 0

            if blocks:
                max_ylevel_top = max(b.ylevel_top for b in blocks)
                span_height = (self.spreadsheet.span_height[y + 1] +
                               self.cellsize * 5 / 2 * (max_ylevel_top - 1) +
                               self.cellsize)
                self.spreadsheet.set_span_height(y + 1, span_height)

            blocks = [b for b in diagram.altblocks if b.edges[-1].order == y]
            if blocks:
                max_ylevel_bottom = max(b.ylevel_bottom for b in blocks)
                span_height = (self.spreadsheet.span_height[y + 2] +
                               self.cellsize / 2 * (max_ylevel_bottom - 1))

                self.spreadsheet.set_span_height(y + 2, span_height)

    def pagesize(self, width=None, height=None):
        width = self.node_count
        height = len(self.edges) + len(self.separators) + 1
        return super(DiagramMetrics, self).pagesize(width, height)

    @property
    def bottomheight(self):
        height = len(self.edges) + len(self.separators)
        dummy = elements.DiagramNode(None)
        dummy.xy = XY(1, height)
        _, y = self.spreadsheet._node_bottomright(dummy, use_padding=False)
        y += self.spreadsheet.span_height[len(self.edges) + 1] / 2
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
        edges = dict([e.order, e] for e in self.edges + self.separators)

        # y coodinates for top of activity box
        starts = activity['lifetime'][0]
        edge = edges[starts]
        y1 = self.edge(edge).baseheight
        if isinstance(edge, elements.DiagramEdge):
            if edge.diagonal and edge.node2 == node:
                y1 += self.edge_height * 3 / 4

        # y coodinates for bottom of activity box
        ends = activity['lifetime'][-1] + 1
        if ends < len(edges):
            y2 = self.edge(edges[ends]).baseheight
        else:
            y2 = self.bottomheight + self.cellsize * 2

        index = activity['level']
        base_x = self.cell(node).bottom.x
        box = (base_x + (index - 1) * self.cellsize / 2, y1,
               base_x + (index + 1) * self.cellsize / 2, y2)

        return box

    def activity_shadow(self, node, activity):
        box = self.activity_box(node, activity)

        return Box(box[0] + self.shadow_offset.x,
                   box[1] + self.shadow_offset.y,
                   box[2] + self.shadow_offset.x,
                   box[3] + self.shadow_offset.y)

    def edge_textsize(self, edge):
        width = 0
        height = 0
        if edge.label:
            if edge.direction == 'self':
                cell = self.cell(edge.node1)
                width = self.edge(edge).right - cell.center.x
            else:
                width = (self.cell(edge.right_node).center.x -
                         self.cell(edge.left_node).center.x)
            width, height = self.textsize(edge.label, width=width,
                                          font=self.font_for(edge))

        return XY(width, height)

    def expand_pagesize_for_note(self, edge):
        if edge.leftnote:
            cell = self.cell(edge.left_node)
            width = cell.center.x - self.cellsize * 6

            if width < edge.leftnotesize.width:
                span_width = edge.leftnotesize.width - width
                self.spreadsheet.span_width[0] += span_width

        if edge.rightnote:
            cell = self.cell(edge.right_node)
            if edge.direction == 'self':
                right = self.edge(edge).right
                width = self.pagesize().x - right - self.cellsize * 3
            else:
                width = self.pagesize().x - cell.center.x - self.cellsize * 3

            if edge.right_node.xy.x + 1 == self.node_count:
                width -= self.cellsize * 2

            if width < edge.rightnotesize.width:
                span_width = edge.rightnotesize.width - width
                self.spreadsheet.span_width[self.node_count] += span_width

    def cell(self, obj, use_padding=True):
        if isinstance(obj, (elements.DiagramEdge, elements.EdgeSeparator)):
            klass = namedtuple('_', 'xy width height colwidth colheight')
            edge = klass(XY(1, obj.order + 1), None, None, 1, 1)
            return super(DiagramMetrics, self).cell(edge, use_padding=False)
        elif isinstance(obj, elements.AltBlock):
            box = super(DiagramMetrics, self).cell(obj, use_padding=False)
            return AltBlockMetrics(self, obj, box)
        else:
            return super(DiagramMetrics, self).cell(obj, use_padding)

    def edge(self, edge):
        if isinstance(edge, elements.EdgeSeparator):
            return self.separator(edge)
        else:
            return EdgeMetrics(edge, self)

    def separator(self, separator):
        return SeparatorMetrics(separator, self)


class AltBlockMetrics(blockdiag.metrics.NodeMetrics):
    def __init__(self, metrics, block, box):
        self.block = block
        sheet = metrics.spreadsheet
        cellsize = metrics.cellsize

        box[0] -= (sheet.span_width[block.xy.x + 1] / 2 -
                   cellsize * (block.xlevel - 1))
        box[1] -= cellsize * 5 / 2 * (block.ylevel_top - 1) + cellsize * 3
        box[2] += (sheet.span_width[block.xy.x + block.colwidth + 2] / 2 -
                   cellsize * (block.xlevel - 1))
        box[3] += cellsize * (block.ylevel_bottom - 1) + cellsize

        super(AltBlockMetrics, self).__init__(metrics, *box)

    @property
    def textbox(self):
        size = self.metrics.textsize(self.block.type,
                                     font=self.metrics.font_for(self.block))
        return Box(self.x1, self.y1,
                   self.x1 + size.width, self.y1 + size.height)


class EdgeMetrics(object):
    def __init__(self, edge, metrics):
        self.metrics = metrics
        self.edge = edge

    @property
    def baseheight(self):
        cell = self.metrics.cell(self.edge)
        if (cell.height == self.edge.leftnotesize.height or
           (cell.height == self.edge.rightnotesize.height)):
            return cell.center.y
        else:
            return cell.top.y + self.edge.textheight

    @property
    def right(self):
        m = self.metrics
        cell = m.cell(self.edge.right_node)

        if self.edge.direction == 'self':

            if self.edge.node1.xy.x + 1 == m.node_count:
                width = cell.width / 2 + m.cellsize * 3
            else:
                span_width = m.spreadsheet.span_width[self.edge.node1.xy.x]
                width = cell.width / 2 + span_width / 2

            x = cell.bottom.x + width
        else:
            x = cell.bottom.x - m.cellsize

            if self.edge.failed:
                x -= self.metrics.edge_length / 2

        return x

    @property
    def shaft(self):
        m = self.metrics
        baseheight = self.baseheight

        if self.edge.direction == 'self':
            cell = m.cell(self.edge.node1)
            fold_height = m.cellsize * 2

            # adjust textbox to right on activity-lines
            base_x = cell.bottom.x
            x1 = base_x + self.activity_line_width(self.edge.node1)
            x2 = self.right

            line = [XY(x1 + m.cellsize, baseheight),
                    XY(x2, baseheight),
                    XY(x2, baseheight + fold_height),
                    XY(x1 + m.cellsize, baseheight + fold_height)]
        else:
            x1 = (self.metrics.node(self.edge.left_node).bottom.x +
                  self.activity_line_width(self.edge.left_node))
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
                self.activity_line_width(self.edge.left_node) + \
                self.metrics.cellsize / 2
        else:  # left
            x = m.node(self.edge.right_node).bottom.x - self.edge.textwidth

        y1 = self.baseheight - self.edge.textheight
        return Box(x, y1, x + self.edge.textwidth, y1 + self.edge.textheight)

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

        x = cell.center.x - m.cellsize * 3 - notesize.width
        y = self.baseheight - notesize.height / 2

        if self.edge.failed and self.edge.direction == 'left':
            x += self.metrics.edge_length / 2 - m.cellsize

        return Box(x, y, x + notesize.width, y + notesize.height)

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
            x = self.right + m.cellsize * 2
        elif self.edge.failed and self.edge.direction == 'right':
            x = self.right + m.cellsize * 4
        else:
            x = cell.center.x + m.cellsize * 2

        notesize = self.edge.rightnotesize
        y = self.baseheight - notesize.height / 2
        return Box(x, y, x + notesize.width, y + notesize.height)

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

        font = metrics.font_for(self)
        size = metrics.textsize(separator.label, font, x2 - x1)
        dx = (x2 - x1 - size.width) / 2
        dy = (y2 - y1 - size.height) / 2
        self.labelbox = Box(x1 + dx - d,
                            y1 + dy - d,
                            x1 + dx + size.width + d,
                            y1 + dy + size.height + d)

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
