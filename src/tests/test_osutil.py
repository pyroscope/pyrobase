""" OS Helper tests.

    Copyright (c) 2018 The PyroScope Project <pyroscope.project@gmail.com>

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

from pyrobase import osutil


class OsUtilTest(unittest.TestCase):

    def test_shell_escape(self):
        cases = [
            ("abc",         "abc"),
            ("123",         "123"),
            ("safe-._,+",   "safe-._,+"),
            ("!bang",       "'!bang'"),
            ("d\"q",        "'d\"q'"),
            ("s'q",         r"'s'\''q'"),
            ("abc",        "abc"),
            ("!bang",      "'!bang'"),
            ("\xA0",       "'\xA0'"),
        ]
        for val, expected in cases:
            result = osutil.shell_escape(val)
            assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
