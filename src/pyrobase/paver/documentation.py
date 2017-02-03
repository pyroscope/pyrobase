# -*- coding: utf-8 -*-
# pylint: disable=expression-not-assigned
""" Paver Documentation Generator Tasks.

    Copyright (c) 2011 The PyroScope Project <pyroscope.project@gmail.com>
"""
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import os
import re
import sys

from paver import easy

from pyrobase.paver import support


@easy.task
@easy.cmdopts([
    ('docs-dir=', 'd', 'directory to put the api documentation in'),
    ('includes=', 'i', 'list of additional packages'),
    ('excludes=', 'x', 'list of packages to exclude'),
])
@support.task_requires("epydoc>=3.0")
def docs():
    "create documentation"
    from epydoc import cli # pylint: disable=W0404

    easy.path('build').exists() or easy.path('build').makedirs()

    # get storage path
    docs_dir = easy.options.docs.get('docs_dir', 'build/apidocs')

    # clean up previous docs
    (easy.path(docs_dir) / "epydoc.css").exists() and easy.path(docs_dir).rmtree()

    # set up includes
    try:
        include_names = easy.options.docs.includes
    except AttributeError:
        include_names = []
    else:
        include_names = include_names.replace(',', ' ').split()

    # set up excludes
    try:
        exclude_names = easy.options.docs.excludes
    except AttributeError:
        exclude_names = []
    else:
        exclude_names = exclude_names.replace(',', ' ').split()

    excludes = []
    for pkg in exclude_names:
        excludes.append("--exclude")
        excludes.append('^' + re.escape(pkg))

    # call epydoc in-process
    sys_argv = sys.argv
    try:
        sys.argv = [
            sys.argv[0] + "::epydoc",
            "-v",
            "--inheritance", "listed",
            "--output", os.path.abspath(docs_dir),
            "--name", "%s %s" % (easy.options.setup.name, easy.options.setup.version),
            "--url", easy.options.setup.url,
            "--graph", "umlclasstree",
        ] + excludes + support.toplevel_packages() + include_names
        sys.stderr.write("Running '%s'\n" % ("' '".join(sys.argv)))
        cli.cli()
    finally:
        sys.argv = sys_argv
