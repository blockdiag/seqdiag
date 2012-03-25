# -*- coding: utf-8 -*-

# Copyright (c) 2008/2009 Andrey Vlasovskikh
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

r'''A DOT language parser using funcparserlib.

The parser is based on [the DOT grammar][1]. It is pretty complete with a few
not supported things:

* Ports and compass points
* XML identifiers

At the moment, the parser builds only a parse tree, not an abstract syntax tree
(AST) or an API for dealing with DOT.

  [1]: http://www.graphviz.org/doc/info/lang.html
'''

import codecs
from re import MULTILINE, DOTALL
from funcparserlib.lexer import make_tokenizer, Token, LexerError
from funcparserlib.parser import (some, a, maybe, many, finished, skip,
                                  forward_decl)
from blockdiag.utils.namedtuple import namedtuple

ENCODING = 'utf-8'

Graph = namedtuple('Graph', 'type id stmts')
SubGraph = namedtuple('SubGraph', 'stmts')
Node = namedtuple('Node', 'id attrs')
Attr = namedtuple('Attr', 'name value')
Edge = namedtuple('Edge', 'nodes attrs subedge')
DefAttrs = namedtuple('DefAttrs', 'object attrs')
AttrClass = namedtuple('AttrClass', 'name attrs')
AttrPlugin = namedtuple('AttrPlugin', 'name attrs')
Separator = namedtuple('Separator', 'type value')


class ParseException(Exception):
    pass


def tokenize(string):
    'str -> Sequence(Token)'
    specs = [
        ('Comment', (r'/\*(.|[\r\n])*?\*/', MULTILINE)),
        ('Comment', (r'(//|#).*',)),
        ('NL',      (r'[\r\n]+',)),
        ('Space',   (r'[ \t\r\n]+',)),
        ('Separator', (r'(?P<sep>===|\.\.\.)[^\r\n]+(?P=sep)',)),
        ('Name',    (ur'[A-Za-z_0-9\u0080-\uffff]'
                     ur'[A-Za-z_\-.0-9\u0080-\uffff]*',)),
        ('Op',      (r'(=>)|[{};,=\[\]]|(<<?--?)|(--?>>?)',)),
        ('Number',  (r'-?(\.[0-9]+)|([0-9]+(\.[0-9]*)?)',)),
        ('String',  (r'(?P<quote>"|\').*?(?<!\\)(?P=quote)', DOTALL)),
    ]
    useless = ['Comment', 'NL', 'Space']
    t = make_tokenizer(specs)
    return [x for x in t(string) if x.type not in useless]


def parse(seq):
    'Sequence(Token) -> object'
    unarg = lambda f: lambda args: f(*args)
    tokval = lambda x: x.value
    flatten = lambda list: sum(list, [])
    n = lambda s: a(Token('Name', s)) >> tokval
    op = lambda s: a(Token('Op', s)) >> tokval
    op_ = lambda s: skip(op(s))
    _id = some(lambda t:
               t.type in ['Name', 'Number', 'String']).named('id') >> tokval
    sep = some(lambda t: t.type == 'Separator').named('sep') >> tokval
    make_graph_attr = lambda args: DefAttrs(u'graph', [Attr(*args)])
    make_edge = lambda x, x2, xs, attrs, subedge: \
        Edge([x, x2] + xs, attrs, subedge)
    make_subedge = lambda args: SubGraph(args)
    make_separator = lambda s: Separator(s[0:3], s[3:-3].strip())

    node_id = _id  # + maybe(port)
    a_list = (
        _id +
        maybe(op_('=') + _id) +
        skip(maybe(op(',')))
        >> unarg(Attr))
    attr_list = (
        many(op_('[') + many(a_list) + op_(']'))
        >> flatten)
    attr_stmt = (
        (n('graph') | n('node') | n('edge')) +
        attr_list
        >> unarg(DefAttrs))
    graph_attr = _id + op_('=') + _id >> make_graph_attr
    node_stmt = node_id + attr_list >> unarg(Node)
    separator_stmt = (sep >> make_separator)

    #  edge statements::
    #     A -> B;
    #     C -> D {
    #       D -> E;
    #     }
    #
    subedge = forward_decl()
    edge_rel = (op('<<--') | op('<--') | op('<<-') | op('<-') |
                op('->') | op('->>') | op('-->') | op('-->>') |
                op('=>'))
    edge_rhs = edge_rel + node_id
    edge_stmt = (
        node_id +
        edge_rhs +
        many(edge_rhs) +
        attr_list +
        maybe(subedge)
        >> unarg(make_edge))
    edge_stmt_list = many((edge_stmt | separator_stmt) + skip(maybe(op(';'))))
    subedge.define(
        op_('{') +
        edge_stmt_list +
        op_('}')
        >> make_subedge)

    #  group statements::
    #     group {
    #        A;
    #     }
    #
    subgraph_stmt = (
        graph_attr
        | node_stmt
    )
    subgraph_stmt_list = many(subgraph_stmt + skip(maybe(op(';'))))
    subgraph = (
        skip(n('group')) +
        skip(maybe(_id)) +
        op_('{') +
        subgraph_stmt_list +
        op_('}')
        >> SubGraph)

    #
    #  graph
    #
    class_stmt = (
        skip(n('class')) +
        node_id +
        attr_list
        >> unarg(AttrClass))
    plugin_stmt = (
        skip(n('plugin')) +
        node_id +
        attr_list
        >> unarg(AttrPlugin))
    stmt = (
        class_stmt
        | plugin_stmt
        | subgraph
        | edge_stmt
        | separator_stmt
        | graph_attr
        | node_stmt
    )
    stmt_list = many(stmt + skip(maybe(op(';'))))
    graph = (
        maybe(n('diagram') | n('seqdiag')) +
        maybe(_id) +
        op_('{') +
        stmt_list +
        op_('}')
        >> unarg(Graph))
    dotfile = graph + skip(finished)

    return dotfile.parse(seq)


def sort_tree(tree):
    def weight(node):
        if isinstance(node, (Attr, DefAttrs, AttrPlugin, AttrClass)):
            return 1
        else:
            return 2

    def compare(node1, node2):
        return cmp(weight(node1), weight(node2))

    if hasattr(tree, 'stmts'):
        tree.stmts.sort(compare)
        for stmt in tree.stmts:
            sort_tree(stmt)

    return tree


def parse_string(string):
    try:
        tree = parse(tokenize(string))
        return sort_tree(tree)
    except LexerError, e:
        message = "Got unexpected token at line %d column %d" % e.place
        raise ParseException(message)
    except Exception, e:
        raise ParseException(str(e))


def parse_file(path):
    code = codecs.open(path, 'r', 'utf-8').read()
    return parse_string(code)
