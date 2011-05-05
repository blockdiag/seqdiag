#!bin/py
# -*- coding: utf-8 -*-

import sys
import blockdiag.DiagramDraw
from blockdiag.utils.XY import XY


class DiagramDraw(blockdiag.DiagramDraw.DiagramDraw):
    def __init__(self, format, diagram, filename=None, **kwargs):
        super(DiagramDraw, self).__init__(format, diagram, filename, **kwargs)

        self.metrix.set_edges(self.diagram.edges)

    def pagesize(self, scaled=False):
        return self.metrix.pageSize(self.nodes, self.diagram.edges)

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
        self.drawer.rectangle(box, width=1, outline=self.fill, fill='moccasin')

    def lifelines(self, node):
        line = self.metrix.originalMetrix().lifeline(node)
        self.drawer.line(line, fill=self.fill, style='dotted')

    def _prepare_edges(self):
        pass

    def edge(self, edge):
        node1_xy = self.metrix.node(edge.node1).bottom()
        node2_xy = self.metrix.node(edge.node2).bottom()

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        m = self.metrix
        baseheight = node1_xy.y + m.spanHeight + \
                     int(edge.y * m.edge_height) + m.edge_height / 2

        if edge.direction == 'self':
            fold_width = m.nodeWidth / 2 + m.cellSize
            fold_height = m.edge_height / 4

            # adjust textbox to right on activity-lines
            x1 = node1_xy.x + self.activity_line_width(edge.node1, edge.y)

            points = [XY(x1 + m.cellSize, baseheight),
                      XY(x1 + fold_width, baseheight),
                      XY(x1 + fold_width, baseheight + fold_height),
                      XY(x1 + m.cellSize, baseheight + fold_height)]

            self.drawer.line(points, fill=color, style=edge.style)
            self.edge_head(points[-1], 'left', color, edge.async)
        else:
            if edge.direction == 'right':
                margin = m.cellSize

                x1, x2 = node1_xy.x, node2_xy.x
                x1 += self.activity_line_width(edge.node1, edge.y)
            else:
                margin = - m.cellSize

                x1, x2 = node2_xy.x, node1_xy.x
                x2 += self.activity_line_width(edge.node2, edge.y)

            _from = XY(x1 + margin, baseheight)
            _to = XY(x2 - margin, baseheight)
            if edge.diagonal:
                _to = XY(_to.x, _to.y + m.edge_height * 3 / 4)
            self.drawer.line((_from, _to), fill=color, style=edge.style)
            self.edge_head(_to, edge.direction, color, edge.async)

    def edge_head(self, xy, direct, fill, async):
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
            self.drawer.line((head[0], head[1]), fill=fill)
            self.drawer.line((head[1], head[2]), fill=fill)
        else:
            self.drawer.polygon(head, outline=fill, fill=fill)

    def edge_label(self, edge):
        node1_xy = self.metrix.node(edge.node1).bottom()
        node2_xy = self.metrix.node(edge.node2).bottom()

        m = self.metrix
        baseheight = node1_xy.y + m.spanHeight + int(edge.y * m.edge_height)

        x1, x2 = node1_xy.x, node2_xy.x
        if node1_xy.x < node2_xy.x:
            left_node = edge.node1
            aligns = ['left', 'right']
        elif node1_xy.x == node2_xy.x:
            x2 = x1 + m.nodeWidth + m.spanWidth
            left_node = edge.node1
            aligns = ['left', 'right']
        else:
            x1, x2 = x2, x1
            left_node = edge.node2
            aligns = ['right', 'left']

        if edge.dir == 'forward':
            halign = aligns[0]
        else:
            halign = aligns[1]

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        # adjust textbox to right on activity-lines
        x1 += self.activity_line_width(left_node, edge.y)

        box = (x1, baseheight,
               x2, baseheight + int(m.edge_height * 0.45))
        self.drawer.textarea(box, edge.label, fill=color, halign=halign,
                             font=self.font, fontsize=m.fontSize)

    def activity_line_width(self, node, index):
        m = self.metrix

        activities = [a for a in node.activities if index in a['lifetime']]
        if activities:
            level = max(a['level'] for a in activities)
        else:
            level = 0

        return m.cellSize / 2 * level


from DiagramMetrix import DiagramMetrix
DiagramDraw.set_metrix_class(DiagramMetrix)
