#!bin/py
# -*- coding: utf-8 -*-

import blockdiag.DiagramMetrix
from blockdiag.utils.XY import XY


class DiagramMetrix(blockdiag.DiagramMetrix.DiagramMetrix):
    def __init__(self, diagram, **kwargs):
        super(DiagramMetrix, self).__init__(diagram, **kwargs)

        scale_ratio = self.scale_ratio
        if diagram.edge_height:
            self.setdefault('edge_height', diagram.edge_height)
        else:
            self.setdefault('edge_height', self.nodeHeight / scale_ratio)

        if diagram.edge_length:
            span_width = diagram.edge_length - self.nodeWidth / scale_ratio
            if span < 0:
                msg = "WARNING: edge_length is too short: %d\n" % \
                      self.diagram.edge_length
                sys.stderr.write(msg)

                span = 0

            self.spanWidth = span

    def originalMetrix(self):
        kwargs = {}
        for key in self:
            kwargs[key] = self[key]
        kwargs['scale_ratio'] = 1

        m = DiagramMetrix(self, **kwargs)
        m.set_edges(self.edges)
        return m

    def set_edges(self, edges):
        self.edges = edges

    def pageSize(self, nodes=None, edges=None):
        if nodes:
            width = max(x.xy.x for x in nodes)
        else:
            width = 0

        size = super(DiagramMetrix, self).pageSize(width + 1, 1)

        if edges is None:
            edges = self.edges

        height = int(sum(e.height for e in edges) * self.edge_height)
        height += self.spanHeight + self.edge_height / 2

        return XY(size.x, size.y + height)

    def groupBox(self, group):
        box = list(self.cell(group).marginBox())
        box[3] = self.pageSize().y - self.pageMargin.y - self.pagePadding[2]

        return box

    def lifeline(self, node):
        y = self.pageSize().y - self.pageMargin.y - self.pagePadding[2]

        pt1 = self.node(node).bottom()
        pt2 = XY(pt1.x, y)

        return [pt1, pt2]

    def activity_box(self, node, activity):
        starts = activity['lifetime'][0]
        ends = activity['lifetime'][-1] + 1

        edge = self.edges[starts]
        (base_x, base_y) = self.cell(node).bottom()
        base_y += self.spanHeight

        y1 = base_y + int(edge.y * self.edge_height) + self.edge_height / 2
        if edge.diagonal and edge.node2 == node:
            y1 += self.edge_height * 3 / 4

        if ends < len(self.edges):
            edge = self.edges[ends]
            y2 = base_y + int(edge.y * self.edge_height) + self.edge_height / 2
        else:
            y2 = self.pageSize().y - self.pageMargin.y - self.edge_height / 2

        index = activity['level']
        box = (base_x + (index - 1) * self.cellSize / 2, y1,
               base_x + (index + 1) * self.cellSize / 2, y2)

        return box

    def activity_shadow(self, node, activity):
        box = self.activity_box(node, activity)

        return (box[0] + self.shadowOffsetX, box[1] + self.shadowOffsetY,
                box[2] + self.shadowOffsetX, box[3] + self.shadowOffsetY)
