#!bin/py
# -*- coding: utf-8 -*-

import os
import re
import sys
import math
from ConfigParser import SafeConfigParser
from optparse import OptionParser
from elements import *
from DiagramDraw import DiagramDraw
import diagparser
from blockdiag.utils.XY import XY


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
        if edge_type:
            edge.setAttributes([diagparser.Attr('dir', edge_type)])
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
            if edge.dir == 'both':
                reverse.style = 'dashed'
                reverse.label = edge.return_label

            group.edges.append(reverse)


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
