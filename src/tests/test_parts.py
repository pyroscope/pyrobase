# pylint: disable=missing-docstring
""" Data Types tests.

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
from __future__ import absolute_import, print_function, unicode_literals

import unittest

import pytest

from pyrobase import parts


class BunchTest(unittest.TestCase):

    def test_janus(self):
        bunch = parts.Bunch()
        bunch.a = 1
        bunch["z"] = 2
        assert bunch["a"] == 1
        assert bunch.z == 2

    def test_repr(self):
        bunch = repr(parts.Bunch(a=1, z=2))
        assert bunch.startswith("Bunch(")
        assert "a=" in bunch
        assert bunch.index("a=") < bunch.index("z=")

    def test_exc(self):
        bunch = parts.Bunch()
        with pytest.raises(AttributeError):
            return bunch.not_there


if __name__ == "__main__":
    pytest.main([__file__])
