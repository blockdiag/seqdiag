#!bin/py
# -*- coding: utf-8 -*-

import os
import re
import sys
from ConfigParser import SafeConfigParser
from optparse import OptionParser
from blockdiag.elements import *
import blockdiag.DiagramDraw
import diagparser
from blockdiag.utils.XY import XY

# blockdiag patch 1: accept 'return' edge attribute like [return = "foo bar"]
DiagramEdgeBase = DiagramEdge


class DiagramEdge(DiagramEdgeBase):
    return_label = None

    def __init__(self, node1, node2):
        DiagramEdgeBase.__init__(self, node1, node2)

        self.dir = 'both'
        self.height = 1
        self.y = 0
        self.diagonal = False
        self.return_label = ''

    def setAttributes(self, attrs):
        attrs = list(attrs)
        for attr in attrs:
            value = unquote(attr.value)

            if attr.name == 'return':
                self.return_label = value
                attrs.remove(attr)
            elif attr.name == 'diagonal':
                self.diagonal = True
                self.height = 1.5
                attrs.remove(attr)

        DiagramEdgeBase.setAttributes(self, attrs)

# blocdiag patch 2: add align option for TextFolder
try:
    from blockdiag.ImageDrawEx import TextFolder as TextFolderBase
except ImportError:
    from blockdiag.SVGImageDraw import TextFolder as TextFolderBase

import math


class TextFolder(TextFolderBase):
    def __init__(self, box, string, **kwargs):
        self.align = kwargs.get('align', 'center')
        if 'align' in kwargs:
            del kwargs['align']
        TextFolderBase.__init__(self, box, string, **kwargs)

    def each_line(self):
        size = XY(self.box[2] - self.box[0], self.box[3] - self.box[1])

        height = int(math.ceil((size.y - self.height()) / 2.0))
        base_xy = XY(self.box[0], self.box[1])

        for string in self._result:
            textsize = self.textsize(string)
            halign = size.x - textsize[0] * self.scale

            if self.adjustBaseline:
                height += textsize[1]

            if self.align == 'left':
                x = 8  # left padding 8 : MAGIC number
            elif self.align == 'right':
                x = halign - 8  # right padding 8 : MAGIC number
            else:
                x = int(math.ceil(halign / 2.0))
            draw_xy = XY(base_xy.x + x, base_xy.y + height)

            yield string, draw_xy

            if self.adjustBaseline:
                height += self.lineSpacing
            else:
                height += textsize[1] + self.lineSpacing

try:
    from blockdiag.ImageDrawEx import ImageDrawEx

    def imagedrawex_textarea(self, box, string, **kwargs):
        lines = TextFolder(box, string, scale=self.scale_ratio, **kwargs)
        for string, xy in lines.each_line():
            self.text(xy, string, **kwargs)

    ImageDrawEx.textarea = imagedrawex_textarea
except ImportError:
    pass


def imagedrawex_textarea(self, box, string, **kwargs):
    lines = TextFolder(box, string, adjustBaseline=True, **kwargs)
    for string, xy in lines.each_line():
        self.text(xy, string, **kwargs)
from blockdiag.SVGImageDraw import SVGImageDraw
SVGImageDraw.textarea = imagedrawex_textarea


class DiagramTreeBuilder:
    def build(self, tree):
        self.diagram = Diagram()
        self.diagram = self.instantiate(self.diagram, tree)

        self.update_y_coordinates()
        max_y = self.diagram.edges[-1].y

        self.diagram.width = len(self.diagram.nodes)
        self.diagram.height = int(math.ceil(max_y * 0.5 + 1.5))

        return self.diagram

    def update_y_coordinates(self):
        height = 0
        for edge in self.diagram.edges:
            edge.y = height
            height += edge.height

    def append_node(self, node):
        if node not in self.diagram.nodes:
            node.xy = XY(len(self.diagram.nodes), 0)
            self.diagram.nodes.append(node)

    def instantiate(self, group, tree):
        for stmt in tree.stmts:
            if isinstance(stmt, diagparser.Node):
                node = DiagramNode.get(stmt.id)
                node.setAttributes(stmt.attrs)
                self.append_node(node)

            elif isinstance(stmt, diagparser.Edge):
                self.instantiate_edge(group, stmt)

            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

        return group

    def instantiate_edge(self, group, tree):
        node_id = tree.nodes[0]
        edge_from = DiagramNode.get(node_id)
        self.append_node(edge_from)

        edge_type, node_id = tree.nodes[1]
        edge_to = DiagramNode.get(node_id)
        self.append_node(edge_to)

        edge = DiagramEdge(edge_from, edge_to)
        edge.setAttributes(tree.attrs)

        if edge.dir in ('forward', 'both'):
            forward = edge.duplicate()
            forward.dir = 'forward'
            group.edges.append(forward)

        if len(tree.nodes) > 2:
            nodes = [edge_to.id] + tree.nodes[2:]
            nested = diagparser.Edge(nodes, tree.attrs, tree.subedge)
            self.instantiate_edge(group, nested)
        elif tree.subedge:
            self.instantiate(group, tree.subedge)

        if edge.dir in ('back', 'both') and edge.node1 != edge.node2:
            reverse = edge.duplicate()
            reverse.dir = 'back'
            reverse.style = 'dashed'
            group.edges.append(reverse)


class DiagramDraw(blockdiag.DiagramDraw.DiagramDraw):
    def __init__(self, format, diagram, **kwargs):
        super(DiagramDraw, self).__init__(format, diagram, **kwargs)

    def _drawBackground(self):
        super(DiagramDraw, self)._drawBackground()

        for node in self.nodes:
            self.lifelines(node)

    def draw(self, **kwargs):
        super(DiagramDraw, self).draw()

        for edge in (x for x in self.edges if not x.label and x.return_label):
            self.edge_label(edge)

    def lifelines(self, node):
        metrix = self.metrix.originalMetrix().node(node)
        pagesize = self.pageSize()

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

            self.drawer.line(points, fill=self.fill)
            self.edge_head(points[-1], 'left')
        else:
            if node1_xy.x < node2_xy.x:
                margin = m.cellSize
                headshape = ['right', 'left']
            else:
                margin = - m.cellSize
                headshape = ['left', 'right']

            if edge.dir in ('forward', 'both'):
                _from = XY(node1_xy.x + margin,
                           baseheight + m.nodeHeight * 0.5)
                _to = XY(node2_xy.x - margin,
                         baseheight + diagonal_cap + m.nodeHeight * 0.5)
                self.drawer.line((_from, _to), fill=self.fill)
                self.edge_head(_to, headshape[0])

            if edge.dir in ('back', 'both'):
                _from = XY(node2_xy.x - margin,
                           baseheight + m.nodeHeight * 0.5)
                _to = XY(node1_xy.x + margin,
                         baseheight + diagonal_cap + m.nodeHeight * 0.5)
                self.drawer.line((_from, _to), fill=self.fill, style='dashed')
                self.edge_head(_to, headshape[1])

    def edge_head(self, xy, direct):
        head = []
        cell = self.metrix.cellSize

        if direct == 'right':
            head.append(xy)
            head.append((xy.x - cell, xy.y - cell / 2))
            head.append((xy.x - cell, xy.y + cell / 2))
        elif direct == 'left':
            head.append(xy)
            head.append((xy.x + cell, xy.y - cell / 2))
            head.append((xy.x + cell, xy.y + cell / 2))

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
            x2 = x1 + m.nodeWidth * 0.5
            aligns = ['left', 'right']
        else:
            x1, x2 = x2, x1
            aligns = ['right', 'left']

        if edge.dir in ('forward', 'both') and edge.label:
            box = (x1, baseheight,
                   x2, baseheight + m.nodeHeight * 0.45)
            self.drawer.textarea(box, edge.label, fill=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize,
                                 align=aligns[0])

        if edge.dir in ('back', 'both') and edge.return_label:
            box = (x1, baseheight,
                   x2, baseheight + m.nodeHeight * 0.45)
            self.drawer.textarea(box, edge.return_label, fill=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize,
                                 align=aligns[1])


def parse_option():
    usage = "usage: %prog [options] infile"
    p = OptionParser(usage=usage)
    p.add_option('-a', '--antialias', action='store_true',
                 help='Pass diagram image to anti-alias filter')
    p.add_option('-c', '--config',
                 help='read configurations from FILE', metavar='FILE')
    p.add_option('-o', dest='filename',
                 help='write diagram to FILE', metavar='FILE')
    p.add_option('-f', '--font', default=[], action='append',
                 help='use FONT to draw diagram', metavar='FONT')
    p.add_option('-P', '--pdb', dest='pdb', action='store_true', default=False,
                 help='Drop into debugger on exception')
    p.add_option('-T', dest='type', default='PNG',
                 help='Output diagram as TYPE format')
    options, args = p.parse_args()

    if len(args) == 0:
        p.print_help()
        sys.exit(0)

    options.type = options.type.upper()
    if not options.type in ('SVG', 'PNG'):
        msg = "ERROR: unknown format: %s\n" % options.type
        sys.stderr.write(msg)
        sys.exit(0)

    if options.config and not os.path.isfile(options.config):
        msg = "ERROR: config file is not found: %s\n" % options.config
        sys.stderr.write(msg)
        sys.exit(0)

    configpath = options.config or "%s/.seqdiagrc" % os.environ.get('HOME')
    if os.path.isfile(configpath):
        config = SafeConfigParser()
        config.read(configpath)

        if config.has_option('seqdiag', 'fontpath'):
            fontpath = config.get('seqdiag', 'fontpath')
            options.font.append(fontpath)

    return options, args


def detectfont(options):
    fonts = options.font + \
            ['c:/windows/fonts/VL-Gothic-Regular.ttf',  # for Windows
             'c:/windows/fonts/msmincho.ttf',  # for Windows
             '/usr/share/fonts/truetype/ipafont/ipagp.ttf',  # for Debian
             '/usr/local/share/font-ipa/ipagp.otf',  # for FreeBSD
             '/System/Library/Fonts/AppleGothic.ttf']  # for MaxOS

    fontpath = None
    for path in fonts:
        if path and os.path.isfile(path):
            fontpath = path
            break

    return fontpath


def main():
    options, args = parse_option()

    infile = args[0]
    if options.filename:
        outfile = options.filename
    else:
        outfile = re.sub('\..*', '', infile) + '.' + options.type.lower()

    if options.pdb:
        sys.excepthook = utils.postmortem

    fontpath = detectfont(options)

    tree = diagparser.parse_file(infile)
    diagram = DiagramTreeBuilder().build(tree)

    draw = DiagramDraw(options.type, diagram, font=fontpath,
                       antialias=options.antialias)
    draw.draw()
    draw.save(outfile)


if __name__ == '__main__':
    main()
