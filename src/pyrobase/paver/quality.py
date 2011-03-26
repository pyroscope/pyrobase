# -*- coding: utf-8 -*-
# pylint: disable=W0106
""" PyroBase - Paver Code Quality Tasks.

    Copyright (c) 2011 The PyroScope Project <pyroscope.project@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
from __future__ import with_statement

import os
import sys

from paver import easy
from pyrobase.paver import support


@easy.task
@easy.cmdopts([
    ('output=', 'o', 'Create report file (.html, .log, or .txt) [stdout]'),
    ('rcfile=', 'r', 'Configuration file [./pylint.cfg]'),
    ('msg-only', 'm', 'Only generate messages (no reports)'),
])
@support.task_requires("pylint>=0.23")
def lint():
    """ Report pylint results.
    """
    from pylint import lint as linter

    # report according to file extension
    reporters = {
        ".html": linter.HTMLReporter,
        ".log": linter.ParseableTextReporter,
        ".txt": linter.TextReporter,
    }

    lint_build_dir = easy.path("build/lint")
    lint_build_dir.exists() or lint_build_dir.makedirs()

    argv = []
    rcfile = easy.options.lint.get("rcfile")
    if not rcfile and easy.path("pylint.cfg").exists():
        rcfile = "pylint.cfg" 
    if rcfile:
        argv += ["--rcfile", os.path.abspath(rcfile)]
    if easy.options.lint.get("msg_only", False):
        argv += ["-rn"]
    argv += [
        "--import-graph", (lint_build_dir / "imports.dot").abspath(),
    ]
    argv += support.toplevel_packages()

    sys.stderr.write("Running %s::pylint '%s'\n" % (sys.argv[0], "' '".join(argv)))
    outfile = easy.options.lint.get("output", None)
    if outfile:
        outfile = os.path.abspath(outfile)

    try:
        with easy.pushd("src" if easy.path("src").exists() else "."):
            if outfile:
                reporter_class = reporters.get(easy.path(outfile).ext, linter.TextReporter)
                sys.stderr.write("Writing output to %r\n" % (str(outfile),))
                linter.Run(argv, reporter=reporter_class(open(outfile, "w")))
            else:
                linter.Run(argv)
    except SystemExit, exc:
        if not exc.code:
            sys.stderr.write("paver::lint - No problems found.\n")
        elif exc.code & 32:
            # usage error (internal error in this code)
            sys.stderr.write("paver::lint - Usage error, bad arguments %r?!\n" % (argv,))
            raise
        else:
            bits = {
                1: "fatal",
                2: "error",
                4: "warning",
                8: "refactor",
                16: "convention",
            }
            sys.stderr.write("paver::lint - Some %s message(s) issued.\n" % (
                ", ".join([text for bit, text in bits.items() if exc.code & bit])
            ))
            if exc.code & 3:
                sys.stderr.write("paver::lint - Exiting due to fatal / error message.\n")
                raise
