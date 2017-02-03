# -*- coding: utf-8 -*-
# pylint: disable=unused-import, wrong-import-position
""" Paver Easy Task Import.

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
# Add a project's "src" to the path, if it exists and isn't there yet
import os
import sys
if os.path.abspath("src") not in sys.path:
    sys.path.insert(0, os.path.abspath("src"))
del os, sys

# Import public symbols
from pyrobase.paver.quality import lint #@UnusedImport
from pyrobase.paver.documentation import docs #@UnusedImport
from pyrobase.paver.housekeeping import clean, dist_clean #@UnusedImport
from pyrobase.paver.support import task_requires as requires #@UnusedImport
