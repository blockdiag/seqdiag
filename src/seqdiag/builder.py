#!bin/py
# -*- coding: utf-8 -*-

import math
from elements import *
import diagparser
from blockdiag.utils.XY import XY


class DiagramTreeBuilder:
    def build(self, tree):
        self.diagram = Diagram()
        self.diagram = self.instantiate(self.diagram, tree)

        self.update_y_coordinates()
        if self.diagram.draw_activation:
            self.create_activities()
        max_y = self.diagram.edges[-1].y

        self.diagram.width = len(self.diagram.nodes)
        self.diagram.height = int(math.ceil(max_y * 0.5 + 1.5))

        return self.diagram

    def update_y_coordinates(self):
        height = 0
        for edge in self.diagram.edges:
            edge.y = height
            height += edge.height

    def create_activities(self):
        first_node = self.diagram.edges[0].node1
        active_nodes = {first_node: 1}

        for i, edge in enumerate(self.diagram.edges):
            if edge.node1 == edge.node2:
                pass
            elif edge.activate == False:
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

    def append_node(self, node):
        if node not in self.diagram.nodes:
            node.xy = XY(len(self.diagram.nodes), 0)
            self.diagram.nodes.append(node)

    def instantiate(self, group, tree):
        for stmt in tree.stmts:
            if isinstance(stmt, diagparser.Node):
                node = DiagramNode.get(stmt.id)
                node.set_attributes(stmt.attrs)
                self.append_node(node)

            elif isinstance(stmt, diagparser.Edge):
                self.instantiate_edge(group, stmt)

            elif isinstance(stmt, diagparser.DefAttrs):
                group.set_attributes(stmt.attrs)

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
            edge.set_attributes([diagparser.Attr('dir', edge_type)])
        edge.set_attributes(tree.attrs)

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


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree):
        return DiagramTreeBuilder().build(tree)
