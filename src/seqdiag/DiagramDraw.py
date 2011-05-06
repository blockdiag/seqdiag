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
        if edge.color:
            color = edge.color
        else:
            color = self.fill

        # render shaft of edges
        m = self.metrix.edge(edge)
        shaft = m.shaft
        self.drawer.line(shaft, fill=color, style=edge.style)

        # render head of edges
        head = m.head
        if edge.async:
            self.drawer.line((head[0], head[1]), fill=color)
            self.drawer.line((head[1], head[2]), fill=color)
        else:
            self.drawer.polygon(head, outline=color, fill=color)

    def edge_label(self, edge):
        if edge.color:
            color = edge.color
        else:
            color = self.fill

        if edge.direction in ('right', 'self'):
            halign = 'left'
        else:
            halign = 'right'

        textbox = self.metrix.edge(edge).textbox
        self.drawer.textarea(textbox, edge.label, fill=color, halign=halign,
                             font=self.font, fontsize=self.metrix.fontSize)


from DiagramMetrix import DiagramMetrix
DiagramDraw.set_metrix_class(DiagramMetrix)
