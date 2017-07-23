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
import logging
import unittest

from pyrobase import parts

log = logging.getLogger(__name__)
log.trace("module loaded")


class BunchTest(unittest.TestCase):

    def test_janus(self):
        b = parts.Bunch()
        b.a = 1
        b["z"] = 2
        assert b["a"] == 1
        assert b.z == 2

    def test_repr(self):
        b = repr(parts.Bunch(a=1, z=2))
        assert b.startswith("Bunch(")
        assert "a=" in b
        assert b.index("a=") < b.index("z=")

    def test_exc(self):
        b = parts.Bunch()
        try:
            b.not_there
        except AttributeError as exc:
            assert "not_there" in str(exc)
        else:
            assert False, "Expected an exception"


if __name__ == "__main__":
    unittest.main()
