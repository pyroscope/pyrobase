# -*- coding: utf-8 -*-
""" Paver Cleanup Tasks.

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
from __future__ import with_statement

import os
import glob

from paver import easy


@easy.task
@easy.cmdopts([
    ('src-dir=', 's', 'directory where the source lives'),
])
@easy.needs("distutils.command.clean")
def clean():
    "take out the trash"
    src_dir = easy.options.setdefault("docs", {}).get('src_dir', None)
    if src_dir is None:
        src_dir = 'src' if easy.path('src').exists() else '.'

    with easy.pushd(src_dir):
        for pkg in set(easy.options.setup.packages) | set(("tests",)):
            for filename in glob.glob(pkg.replace('.', os.sep) + "/*.py[oc~]"):
                easy.path(filename).remove()


@easy.task
@easy.needs("clean")
def dist_clean():
    "clean up, including dist directory"
    easy.path("dist").rmtree()
