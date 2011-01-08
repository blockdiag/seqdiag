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

        _from = XY(node1_xy.x + m.cellSize,
                   baseheight + m.nodeHeight * 0.5)
        _to = XY(node2_xy.x - m.cellSize,
                 baseheight + m.nodeHeight * 0.5)
        self.drawer.line((_from, _to), fill=self.fill)
        self.edge_head(_to, 'right')

        _from = XY(node2_xy.x - m.cellSize,
                   baseheight + m.nodeHeight)
        _to = XY(node1_xy.x + m.cellSize,
                 baseheight + m.nodeHeight)
        self.drawer.line((_from, _to), fill=self.fill, style='dashed')
        self.edge_head(_to, 'left')

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
        if not edge.label:
            return

        for i, e in enumerate(self.edges):
            if e == edge:
                break

        node1_xy = self.metrix.node(edge.node1).top()
        node2_xy = self.metrix.node(edge.node2).top()

        m = self.metrix
        baseheight = node1_xy.y + (m.nodeHeight + m.spanHeight) * (i + 1)

        box = (node1_xy.x, baseheight,
               node2_xy.x, baseheight + m.nodeHeight * 0.45)
        self.drawer.label(box, edge.label, fill=self.fill,
                          font=self.font, fontsize=self.metrix.fontSize)


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
