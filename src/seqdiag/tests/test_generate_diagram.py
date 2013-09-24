# -*- coding: utf-8 -*-

import os
import sys
import re
import tempfile
import seqdiag.command
from seqdiag.elements import *
from blockdiag.tests.utils import supported_pil, stderr_wrapper


def extra_case(func):
    filename = "VL-PGothic-Regular.ttf"
    testdir = os.path.dirname(__file__)
    pathname = "%s/truetype/%s" % (testdir, filename)

    if os.path.exists(pathname):
        func.__test__ = True
    else:
        func.__test__ = False

    return func


@stderr_wrapper
def __build_diagram(filename, format, additional_args):
    testdir = os.path.dirname(__file__)
    diagpath = "%s/diagrams/%s" % (testdir, filename)

    fontfile = "VL-PGothic-Regular.ttf"
    fontpath = "%s/truetype/%s" % (testdir, fontfile)

    try:
        tmpdir = tempfile.mkdtemp()
        tmpfile = tempfile.mkstemp(dir=tmpdir)
        os.close(tmpfile[0])

        args = ['-T', format, '-o', tmpfile[1], diagpath]
        if additional_args:
            if isinstance(additional_args[0], (list, tuple)):
                args += additional_args[0]
            else:
                args += additional_args
        if os.path.exists(fontpath):
            args += ['-f', fontpath]

        seqdiag.command.main(args)

        if re.search('ERROR', sys.stderr.getvalue()):
            raise RuntimeError(sys.stderr.getvalue())
    finally:
        for file in os.listdir(tmpdir):
            os.unlink(tmpdir + "/" + file)
        os.rmdir(tmpdir)


def diagram_files():
    testdir = os.path.dirname(__file__)
    pathname = "%s/diagrams/" % testdir

    skipped = ['errors',
               'white.gif']

    return [d for d in os.listdir(pathname) if d not in skipped]


def test_generator_svg():
    args = []
    if not supported_pil():
        args.append('--ignore-pil')

    for testcase in generator_core('svg', args):
        yield testcase


@extra_case
def test_generator_png():
    for testcase in generator_core('png'):
        yield testcase


@extra_case
def test_generator_pdf():
    try:
        import reportlab.pdfgen.canvas
        reportlab.pdfgen.canvas
        for testcase in generator_core('pdf'):
            yield testcase
    except ImportError:
        sys.stderr.write("Skip testing about pdf exporting.\n")
        pass


def generator_core(_format, *args):
    for diagram in diagram_files():
        yield __build_diagram, diagram, _format, args

        if re.search('separate', diagram):
            _args = list(args) + ['--separate']
            yield __build_diagram, diagram, _format, _args

        if _format == 'png':
            _args = list(args) + ['--antialias']
            yield __build_diagram, diagram, _format, _args
