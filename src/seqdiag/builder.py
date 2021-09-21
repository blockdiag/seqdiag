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

from blockdiag.utils import XY, unquote

from seqdiag import parser
from seqdiag.elements import (AltBlock, Diagram, DiagramEdge, DiagramNode,
                              EdgeSeparator, NodeGroup)


class DiagramTreeBuilder(object):
    def build(self, tree):
        self.diagram = Diagram()
        self.diagram = self.instantiate(self.diagram, None, tree)

        self.update_node_order()
        self.update_edge_order()
        self.update_altblock_ylevel()
        self.diagram.colwidth = len(self.diagram.nodes)
        self.diagram.colheight = len(self.diagram.edges) + 1

        for sep in self.diagram.separators:
            self.diagram.edges.remove(sep)

        if self.diagram.activation != 'none':
            self.create_activities()

        if self.diagram.autonumber:
            self.update_label_numbered()

        return self.diagram

    def update_edge_order(self):
        for i, edge in enumerate(self.diagram.edges):
            edge.order = i

        height = len(self.diagram.edges) + 1
        for group in self.diagram.groups:
            group.colheight = height

    def update_altblock_ylevel(self):
        altblocks = self.diagram.altblocks
        for i in range(len(self.diagram.edges) + 1):
            blocks = [b for b in altblocks if b.edges[0].order == i]
            for j, altblock in enumerate(reversed(blocks)):
                altblock.ylevel_top = j + 1

            blocks = [b for b in altblocks if b.edges[-1].order == i]
            for j, altblock in enumerate(reversed(blocks)):
                altblock.ylevel_bottom = j + 1

    def update_label_numbered(self):
        for i, edge in enumerate(self.diagram.edges):
            edge.label = "%d. %s" % (i + 1, edge.label or "")

    def create_activities(self):
        if len(self.diagram.edges) == 0:
            return

        first_node = self.diagram.edges[0].node1
        active_nodes = {first_node: 1}
        for node in self.diagram.nodes:
            if node.activated:
                active_nodes[node] = 1

        edge_count = len(self.diagram.edges) + len(self.diagram.separators)
        for i in range(edge_count):
            match = [e for e in self.diagram.edges if e.order == i]
            if match:
                edge = match[0]
                if edge.activate is False:
                    pass
                elif edge.dir == 'forward':
                    if edge.node2 in active_nodes:
                        active_nodes[edge.node2] += 1
                    else:
                        active_nodes[edge.node2] = 1
                elif edge.dir == 'back':
                    if edge.node2 in active_nodes:
                        active_nodes[edge.node2] -= 1
                    else:
                        active_nodes[edge.node2] = 0

            for node in active_nodes:
                if active_nodes[node] > 0:
                    for index in range(active_nodes[node]):
                        node.activate(i, index)

        for node in self.diagram.nodes:
            node.deactivate()

    def update_node_order(self):
        x = 0
        uniq = []

        for node in self.diagram.nodes:
            if node not in uniq:
                node.xy = XY(x, 0)
                uniq.append(node)
                x += 1

                if node.group:
                    for subnode in node.group.nodes:
                        if subnode not in uniq:
                            subnode.xy = XY(x, 0)
                            uniq.append(subnode)
                            x += 1

        for group in self.diagram.groups:
            x = min(node.xy.x for node in group.nodes)
            group.xy = XY(x, 0)
            group.colwidth = len(group.nodes)

    def append_node(self, node, group):
        if node not in self.diagram.nodes:
            self.diagram.nodes.append(node)

        if isinstance(group, NodeGroup) and node not in group.nodes:
            if node.group:
                msg = "DiagramNode could not belong to two groups"
                raise RuntimeError(msg)

            group.nodes.append(node)
            node.group = group

    def instantiate(self, group, block, tree):
        for stmt in tree.stmts:
            if isinstance(stmt, parser.Node):
                node = DiagramNode.get(stmt.id)
                node.set_attributes(stmt.attrs)
                self.append_node(node, group)

            elif isinstance(stmt, parser.Edge):
                self.instantiate_edge(group, block, stmt)

            elif isinstance(stmt, parser.Group):
                node = NodeGroup.get(None)
                self.instantiate(node, block, stmt)
                self.diagram.groups.append(node)

            elif isinstance(stmt, parser.Attr):
                if block:
                    block.set_attribute(stmt)
                else:
                    group.set_attribute(stmt)

            elif isinstance(stmt, parser.Separator):
                sep = EdgeSeparator(stmt.type, unquote(stmt.value), stmt.href)
                sep.group = group
                self.diagram.separators.append(sep)
                group.edges.append(sep)

            elif isinstance(stmt, parser.Fragment):
                subblock = AltBlock(stmt.type, stmt.id)
                if block:
                    subblock.xlevel = block.xlevel + 1
                self.diagram.altblocks.append(subblock)

                self.instantiate(group, subblock, stmt)
                if block:
                    for edge in subblock.edges:
                        block.edges.append(edge)

            elif isinstance(stmt, parser.Extension):
                if stmt.type == 'class':
                    name = unquote(stmt.name)
                    Diagram.classes[name] = stmt
                elif stmt.type == 'plugin':
                    self.diagram.set_plugin(stmt.name, stmt.attrs)

        return group

    def instantiate_edge(self, group, block, stmt):
        from_node = DiagramNode.get(stmt.from_node)
        self.append_node(from_node, group)

        to_node = DiagramNode.get(stmt.to_node)
        self.append_node(to_node, group)

        edge = DiagramEdge(from_node, to_node)
        edge.set_dir(stmt.edge_type)
        edge.set_attributes(stmt.attrs)

        if edge.dir in ('forward', 'both'):
            forward = edge.duplicate()
            forward.dir = 'forward'
            group.edges.append(forward)
            if block:
                block.edges.append(forward)

        if stmt.followers:
            followers = list(stmt.followers)
            next_edge_type, next_to_node = followers.pop(0)
            nested = parser.Edge(stmt.to_node, next_edge_type, next_to_node,
                                 followers, stmt.attrs, stmt.edge_block)
            self.instantiate_edge(group, block, nested)
        elif stmt.edge_block:
            self.instantiate(group, block, stmt.edge_block)

        if edge.dir in ('back', 'both'):
            reverse = edge.duplicate()
            reverse.dir = 'back'
            if edge.dir == 'both':
                reverse.style = 'dashed'
                reverse.label = edge.return_label
                reverse.leftnote = None
                reverse.rightnote = None

            group.edges.append(reverse)
            if block:
                block.edges.append(reverse)


class ScreenNodeBuilder(object):
    @classmethod
    def build(cls, tree):
        DiagramNode.clear()
        DiagramEdge.clear()
        NodeGroup.clear()

        return DiagramTreeBuilder().build(tree)
