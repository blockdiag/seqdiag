#!bin/py
# -*- coding: utf-8 -*-

import os
import re
import sys
import uuid
from ConfigParser import SafeConfigParser
from optparse import OptionParser
from blockdiag.elements import *
import blockdiag.DiagramDraw
from blockdiag import diagparser
from blockdiag.utils.XY import XY

# blockdiag patch 1: accept 'return' edge attribute like [return = "foo bar"]
from blockdiag.ImageDrawEx import ImageDrawEx
DiagramEdgeBase = DiagramEdge
class DiagramEdge(DiagramEdgeBase):

    return_label = None

    def setAttributes(self, attrs):
        for attr in attrs:
            value = unquote(attr.value)

            if attr.name == 'return':
                self.return_label = value
                attrs.remove(attr)

        if not [attr for attr in attrs if attr.name == 'dir']:
            attrs.append(diagparser.Attr('dir', 'both'))

        DiagramEdgeBase.setAttributes(self, attrs)

# blocdiag patch 2: add align option for TextFolder
from blockdiag.ImageDrawEx import TextFolder as TextFolderBase
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

def imagedrawex_textarea(self, box, string, **kwargs):
    lines = TextFolder(box, string, scale=self.scale_ratio, **kwargs)
    for string, xy in lines.each_line():
        self.text(xy, string, **kwargs)
ImageDrawEx.textarea = imagedrawex_textarea


class DiagramTreeBuilder:
    def build(self, tree):
        self.diagram = Diagram()
        self.diagram = self.instantiate(self.diagram, tree)

        self.diagram.width = len(self.diagram.nodes)
        self.diagram.height = len(self.diagram.edges) + 1

        return self.diagram

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
                edge_from = DiagramNode.get(stmt.nodes.pop(0))
                self.append_node(edge_from)

                while len(stmt.nodes):
                    edge_type, edge_to = stmt.nodes.pop(0)
                    edge_to = DiagramNode.get(edge_to)
                    self.append_node(edge_to)

                    edge = DiagramEdge(edge_from, edge_to)
                    edge.setAttributes(stmt.attrs)
                    group.edges.append(edge)

                    edge_from = edge_to

            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

        return group


class DiagramDraw(blockdiag.DiagramDraw.DiagramDraw):
    def __init__(self, format, diagram, **kwargs):
        super(DiagramDraw, self).__init__(format, diagram, **kwargs)

    def _drawBackground(self):
        super(DiagramDraw, self)._drawBackground()

        for node in self.nodes:
            self.lifelines(node)

    def lifelines(self, node):
        metrix = self.metrix.originalMetrix().node(node)
        pagesize = self.pageSize()

        _from = metrix.bottom()
        _to = XY(_from.x, pagesize.y)
        self.drawer.line((_from, _to), fill=self.fill, style='dotted')

    def edge(self, edge):
        for i, e in enumerate(self.edges):
            if e == edge:
                break

        node1_xy = self.metrix.node(edge.node1).top()
        node2_xy = self.metrix.node(edge.node2).top()

        m = self.metrix
        baseheight = node1_xy.y + (m.nodeHeight + m.spanHeight) * (i + 1)

        if edge.node1 == edge.node2:
            points = []
            points.append(XY(node1_xy.x + m.cellSize,
                             baseheight + m.nodeHeight * 0.5))
            points.append(XY(node1_xy.x + m.nodeWidth * 0.5 + m.cellSize,
                             baseheight + m.nodeHeight * 0.5))
            points.append(XY(node1_xy.x + m.nodeWidth * 0.5 + m.cellSize,
                             baseheight + m.nodeHeight))
            points.append(XY(node1_xy.x + m.cellSize,
                             baseheight + m.nodeHeight))

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
                         baseheight + m.nodeHeight * 0.5)
                self.drawer.line((_from, _to), fill=self.fill)
                self.edge_head(_to, headshape[0])

            if edge.dir in ('back', 'both'):
                _from = XY(node2_xy.x - margin,
                           baseheight + m.nodeHeight)
                _to = XY(node1_xy.x + margin,
                         baseheight + m.nodeHeight)
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
        for i, e in enumerate(self.edges):
            if e == edge:
                break

        node1_xy = self.metrix.node(edge.node1).top()
        node2_xy = self.metrix.node(edge.node2).top()

        m = self.metrix
        baseheight = node1_xy.y + (m.nodeHeight + m.spanHeight) * (i + 1)

        xx = (node1_xy.x, node2_xy.x)

        if edge.label:
            box = (min(xx), baseheight,
                   max(xx), baseheight + m.nodeHeight * 0.45)
            self.drawer.textarea(box, edge.label, fill=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize,
                                 align='left')

        if edge.return_label:
            box = (min(xx), int(baseheight + m.nodeHeight * 0.5),
                   max(xx), int(baseheight + m.nodeHeight * 1.0))
            self.drawer.textarea(box, edge.return_label, fill=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize,
                                 align='right')


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
    edges = diagram.edges
    #diagram.edges = []

    draw = DiagramDraw(options.type, diagram, font=fontpath,
                       antialias=options.antialias)

    draw.draw()
    draw.save(outfile)


if __name__ == '__main__':
    main()
