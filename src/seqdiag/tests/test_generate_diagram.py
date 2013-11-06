# -*- coding: utf-8 -*-

import os
import seqdiag.command
from blockdiag.tests.test_generate_diagram import (
    get_diagram_files, testcase_generator
)


def test_generate():
    mainfunc = seqdiag.command.main
    basepath = os.path.dirname(__file__)
    files = get_diagram_files(basepath)
    options = []

    for testcase in testcase_generator(basepath, mainfunc, files, options):
        yield testcase
