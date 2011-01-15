#!bin/py
# -*- coding: utf-8 -*-

import blockdiag.DiagramDraw
from blockdiag.utils.XY import XY


class DiagramDraw(blockdiag.DiagramDraw.DiagramDraw):
    def __init__(self, format, diagram, **kwargs):
        super(DiagramDraw, self).__init__(format, diagram, **kwargs)

    def _draw_background(self):
        for node in self.nodes:
            for activity in node.activities:
                self.node_activity_shadow(node, activity)

        super(DiagramDraw, self)._draw_background()

        for node in self.nodes:
            self.lifelines(node)

            for activity in node.activities:
                self.node_activity(node, activity)

    def node_activity_box(self, node, activity):
        starts = activity['lifetime'][0]
        ends = activity['lifetime'][-1] + 1
        m = self.metrix

        edge = self.diagram.edges[starts]
        node_xy = self.metrix.node(node).top()
        y1 = node_xy.y + \
             int((m.nodeHeight + m.spanHeight) * (edge.y * 0.5 + 1)) + \
             m.nodeHeight * 0.5
        if edge.diagonal and edge.node2 == node:
            y1 += int(m.nodeHeight * 0.75)

        if ends < len(self.diagram.edges):
            edge = self.diagram.edges[ends]
            y2 = node_xy.y + \
                 int((m.nodeHeight + m.spanHeight) * (edge.y * 0.5 + 1)) + \
                 m.nodeHeight * 0.5
        else:
            y2 = self.pagesize().y - m.spanHeight * 0.5

        metrix = self.metrix.node(node)
        x = metrix.bottom().x
        index = activity['level']
        box = (x + (index - 1) * m.cellSize / 2, y1,
               x + (index + 1) * m.cellSize / 2, y2)

        return box

    def node_activity_shadow(self, node, activity):
        m = self.metrix

        if hasattr(m, 'shadowOffsetX'):
            shadowOffsetX = m.shadowOffsetX
            shadowOffsetY = m.shadowOffsetY
        else:
            shadowOffsetX = 6
            shadowOffsetY = 3

        box = self.node_activity_box(node, activity)
        shadowbox = (box[0] + shadowOffsetX, box[1] + shadowOffsetY,
                     box[2] + shadowOffsetX, box[3] + shadowOffsetY)
        self.drawer.rectangle(shadowbox, fill=self.shadow,
                              filter='transp-blur')

    def node_activity(self, node, activity):
        m = self.metrix

        box = self.node_activity_box(node, activity)
        self.drawer.rectangle(box, outline=self.fill, fill='moccasin')

    def lifelines(self, node):
        metrix = self.metrix.originalMetrix().node(node)
        pagesize = self.pagesize()

        _from = metrix.bottom()
        _to = XY(_from.x, pagesize.y)
        self.drawer.line((_from, _to), fill=self.fill, style='dotted')

    def edge(self, edge):
        node1_xy = self.metrix.node(edge.node1).top()
        node2_xy = self.metrix.node(edge.node2).top()

        m = self.metrix
        baseheight = node1_xy.y + \
                int((m.nodeHeight + m.spanHeight) * (edge.y * 0.5 + 1))
        diagonal_cap = 0
        if edge.diagonal:
            diagonal_cap = int(m.nodeHeight * 0.75)

        if edge.node1 == edge.node2:
            points = []
            points.append(XY(node1_xy.x + m.cellSize,
                             baseheight + m.nodeHeight * 0.5))
            points.append(XY(node1_xy.x + m.nodeWidth * 0.5 + m.cellSize,
                             baseheight + m.nodeHeight * 0.5))
            points.append(XY(node1_xy.x + m.nodeWidth * 0.5 + m.cellSize,
                             baseheight + m.nodeHeight * 0.75))
            points.append(XY(node1_xy.x + m.cellSize,
                             baseheight + m.nodeHeight * 0.75))

            self.drawer.line(points, fill=self.fill, style=edge.style)
            self.edge_head(points[-1], 'left', edge.async)
        else:
            if node1_xy.x < node2_xy.x:
                margin = m.cellSize
                headshapes = ['right', 'left']
            else:
                margin = - m.cellSize
                headshapes = ['left', 'right']

            if edge.dir == 'forward':
                x1, x2 = node1_xy.x, node2_xy.x
                headshape = headshapes[0]
            else:
                x1, x2 = node2_xy.x, node1_xy.x
                headshape = headshapes[1]

            if x1 < x2:
                margin = m.cellSize
            else:
                margin = - m.cellSize

            _from = XY(x1 + margin,
                       baseheight + m.nodeHeight * 0.5)
            _to = XY(x2 - margin,
                     baseheight + diagonal_cap + m.nodeHeight * 0.5)
            self.drawer.line((_from, _to), fill=self.fill, style=edge.style)
            self.edge_head(_to, headshape, edge.async)

    def edge_head(self, xy, direct, async):
        head = []
        cell = self.metrix.cellSize

        if direct == 'right':
            head.append(XY(xy.x - cell, xy.y - cell / 2))
            head.append(xy)
            head.append(XY(xy.x - cell, xy.y + cell / 2))
        elif direct == 'left':
            head.append(XY(xy.x + cell, xy.y - cell / 2))
            head.append(xy)
            head.append(XY(xy.x + cell, xy.y + cell / 2))

        if async:
            self.drawer.line((head[0], head[1]), fill=self.fill)
            self.drawer.line((head[1], head[2]), fill=self.fill)
        else:
            self.drawer.polygon(head, outline=self.fill, fill=self.fill)

    def edge_label(self, edge):
        node1_xy = self.metrix.node(edge.node1).top()
        node2_xy = self.metrix.node(edge.node2).top()

        m = self.metrix
        baseheight = node1_xy.y + \
                int((m.nodeHeight + m.spanHeight) * (edge.y * 0.5 + 1))

        x1, x2 = node1_xy.x, node2_xy.x
        if node1_xy.x < node2_xy.x:
            aligns = ['left', 'right']
        elif node1_xy.x == node2_xy.x:
            x2 = x1 + m.nodeWidth + m.spanWidth
            aligns = ['left', 'right']
        else:
            x1, x2 = x2, x1
            aligns = ['right', 'left']

        if edge.dir in ('forward', 'both') and edge.label:
            box = (x1, baseheight,
                   x2, baseheight + m.nodeHeight * 0.45)
            self.drawer.textarea(box, edge.label, fill=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize,
                                 halign=aligns[0])

        if edge.dir in ('back', 'both') and edge.label:
            box = (x1, baseheight,
                   x2, baseheight + m.nodeHeight * 0.45)
            self.drawer.textarea(box, edge.label, fill=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize,
                                 halign=aligns[1])
