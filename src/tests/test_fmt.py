""" PyroBase - Formatting Helper tests.

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

from pyrobase import fmt

log = logging.getLogger(__name__)
log.trace("module loaded")


class FmtTest(unittest.TestCase):

    def test_human_size(self):
        cases = [
            (0,         "   0 bytes"),
            ("123",     " 123 bytes"),
            (123,       " 123 bytes"),
            (-1,        "-??? bytes"),
            (1023,      "1023 bytes"),
            (1024**1,   "   1.0 KiB"),
            (1024**2,   "   1.0 MiB"),
            (1024**3,   "   1.0 GiB"),
            (1024**4,   "1024.0 GiB"),
            (1024**2-51,    "1024.0 KiB"),
            (1024**2-52,    "1023.9 KiB"),
            (1024**2-512,   "1023.5 KiB"),
            #(, ""),
        ]
        for val, expected in cases:
            result = fmt.human_size(val)
            assert result == expected
    
    def test_iso_datetime(self):
        result = (fmt.iso_datetime(0), fmt.iso_datetime(12*3600), fmt.iso_datetime(23*3600))
        assert any("1970-01-01 " in i for i in result)
    
    def test_iso_datetime_optional(self):
        result = (fmt.iso_datetime(86400), fmt.iso_datetime_optional(86400))
        assert result[0] == result[1]
        result = [fmt.iso_datetime_optional(i) for i in (0, "", None, False)]
        assert all(i == "never" for i in result)
    
    def test_human_duration(self):
        cases = [
            ((0,),          "never"),
            #(, ""),
        ]
        for val, expected in cases:
            result = fmt.human_duration(*val)
            assert result == expected
    
    def test_to_unicode(self):
        pass
    
    def test_to_utf8(self):
        pass
    
    def test_to_console(self):
        pass
    

if __name__ == "__main__":
    unittest.main()
