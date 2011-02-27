#!bin/py
# -*- coding: utf-8 -*-

import sys
import blockdiag.DiagramDraw
from blockdiag.utils.XY import XY


class DiagramDraw(blockdiag.DiagramDraw.DiagramDraw):
    def __init__(self, format, diagram, filename=None, **kwargs):
        super(DiagramDraw, self).__init__(format, diagram, filename, **kwargs)

    def preset_metrix(self):
        if self.diagram.edge_height:
            self.edge_height = self.diagram.edge_height
        else:
            self.edge_height = self.metrix.nodeHeight

        if self.diagram.edge_length:
            span = self.diagram.edge_length - self.metrix.nodeWidth
            if span < 0:
                msg = "WARNING: edge_length is too short: %d\n" % \
                      self.diagram.edge_length
                sys.stderr.write(msg)

                span = 0

            self.metrix.spanWidth = span

    def pagesize(self, scaled=False):
        self.preset_metrix()

        if scaled:
            m = self.metrix
        else:
            m = self.metrix.originalMetrix()

        node = max(self.nodes, key=lambda x: x.xy.x)
        xy = m.cell(node).bottomRight()
        x = xy.x + m.pageMargin.x
        y = xy.y + m.spanHeight + self.edge_height / 2 + m.pageMargin.y

        y += len(self.diagram.edges) * self.edge_height

        return XY(x, y)

    def _draw_background(self):
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

    def node_activity_box(self, node, activity):
        starts = activity['lifetime'][0]
        ends = activity['lifetime'][-1] + 1
        m = self.metrix

        edge = self.diagram.edges[starts]
        base_xy = self.metrix.cell(node).bottom()
        base_y = base_xy.y + m.spanHeight
        y1 = base_y + edge.y * self.edge_height + self.edge_height / 2
        if edge.diagonal and edge.node2 == node:
            y1 += self.edge_height * 3 / 4

        if ends < len(self.diagram.edges):
            edge = self.diagram.edges[ends]
            y2 = base_y + edge.y * self.edge_height + self.edge_height / 2
        else:
            y2 = self.pagesize().y - m.pageMargin.y - self.edge_height / 2

        x = base_xy.x
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
        _to = XY(_from.x, pagesize.y - self.metrix.pageMargin.y)
        self.drawer.line((_from, _to), fill=self.fill, style='dotted')

    def edge(self, edge):
        node1_xy = self.metrix.node(edge.node1).bottom()
        node2_xy = self.metrix.node(edge.node2).bottom()

        m = self.metrix
        baseheight = node1_xy.y + m.spanHeight + \
                     edge.y * self.edge_height + self.edge_height / 2

        if edge.node1 == edge.node2:
            fold_width = m.nodeWidth * 0.5 + m.cellSize
            fold_height = self.edge_height * 0.25

            points = [XY(node1_xy.x + m.cellSize, baseheight),
                      XY(node1_xy.x + fold_width, baseheight),
                      XY(node1_xy.x + fold_width, baseheight + fold_height),
                      XY(node1_xy.x + m.cellSize, baseheight + fold_height)]

            self.drawer.line(points, fill=self.fill, style=edge.style)
            self.edge_head(points[-1], 'left', edge.async)
        else:
            if node1_xy.x < node2_xy.x:
                headshapes = ['right', 'left']
            else:
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

            _from = XY(x1 + margin, baseheight)
            _to = XY(x2 - margin, baseheight)
            if edge.diagonal:
                _to = XY(_to.x, _to.y + self.edge_height * 3 / 4)
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
        node1_xy = self.metrix.node(edge.node1).bottom()
        node2_xy = self.metrix.node(edge.node2).bottom()

        m = self.metrix
        baseheight = node1_xy.y + m.spanHeight + edge.y * self.edge_height

        x1, x2 = node1_xy.x, node2_xy.x
        if node1_xy.x < node2_xy.x:
            aligns = ['left', 'right']
        elif node1_xy.x == node2_xy.x:
            x2 = x1 + m.nodeWidth + m.spanWidth
            aligns = ['left', 'right']
        else:
            x1, x2 = x2, x1
            aligns = ['right', 'left']

        if edge.dir == 'forward':
            halign = aligns[0]
        else:
            halign = aligns[1]

        box = (x1, baseheight,
               x2, baseheight + self.edge_height * 0.45)
        self.drawer.textarea(box, edge.label, fill=self.fill, halign=halign,
                             font=self.font, fontsize=m.fontSize)
