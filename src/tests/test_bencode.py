""" Bencode tests.

    List of test cases taken from original BitTorrent code by Bram Cohen.

    Copyright (c) 2009, 2011 The PyroScope Project <pyroscope.project@gmail.com>
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
from __future__ import absolute_import, print_function  #, unicode_literals

import logging
import unittest

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

from pyrobase.testing import mockedopen
from pyrobase.bencode import * #@UnusedWildImport

log = logging.getLogger(__name__)
log.trace("module loaded")


class DecoderTest(unittest.TestCase):

    def test_errors(self):
        testcases = (
            b"",
            b"0:0:",
            b"ie",
            b"i341foo382e",
            #"i-0e",
            b"i123",
            b"i6easd",
            b"35208734823ljdahflajhdf",
            b"2:abfdjslhfld",
            #"02:xy",
            b"l",
            b"l0:",
            b"leanfdldjfh",
            b"relwjhrlewjh",
            b"d",
            b"defoobar",
            b"d3:fooe",
            #"di1e0:e",
            #"d1:b0:1:a0:e",
            #"d1:a0:1:a0:e",
            #"i03e",
            #"l01:ae",
            b"9999:x",
            b"l0:",
            b"d0:0:",
            b"d0:",
        )
        for testcase in testcases:
            #print testcase
            self.failUnlessRaises(BencodeError, bdecode, testcase)


    def test_values(self):
        testcases = (
            (b"i4e", 4),
            (b"i0e", 0),
            (b"i123456789e", 123456789),
            (b"i-10e", -10),
            (b"0:", ''),
            (b"3:abc", "abc"),
            (b"10:1234567890", "1234567890"),
            (b"le", []),
            (b"l0:0:0:e", ['', '', '']),
            (b"li1ei2ei3ee", [1, 2, 3]),
            (b"l3:asd2:xye", ["asd", "xy"]),
            (b"ll5:Alice3:Bobeli2ei3eee", [["Alice", "Bob"], [2, 3]]),
            (b"de", {}),
            (b"d3:agei25e4:eyes4:bluee", {"age": 25, "eyes": "blue"}),
            (b"d8:spam.mp3d6:author5:Alice6:lengthi100000eee",
                {"spam.mp3": {"author": "Alice", "length": 100000}}),
        )
        for bytestring, result in testcases:
            self.failUnlessEqual(bdecode(bytestring), result)

    def test_encoding(self):
        self.failUnlessEqual(bdecode(b"l1:\x801:\x81e", "cp1252"), [u"\u20ac", b"\x81"])

    def test_bread_stream(self):
        self.failUnlessEqual(bread(BytesIO(b"de")), {})

    def test_bread_file(self):
        with mockedopen(fakefiles={"empty_dict": "de"}, mode='b'):
            self.failUnlessEqual(bread("empty_dict"), {})


class EncoderTest(unittest.TestCase):

    def test_errors(self):
        testcases = (
            ({1: b"foo"}, b"d1:13:fooe"),
        )
        for testcase in testcases:
            #print testcase
            self.failUnlessRaises(BencodeError, bencode, testcase)

    def test_values(self):
        testcases = (
            (4, b"i4e"),
            (0, b"i0e"),
            (-10, b"i-10e"),
            (12345678901234567890, b"i12345678901234567890e"),
            (b"", b"0:"),
            (b"abc", b"3:abc"),
            (b"1234567890", b"10:1234567890"),
            ([], b"le"),
            ([1, 2, 3], b"li1ei2ei3ee"),
            ([[b"Alice", b"Bob"], [2, 3]], b"ll5:Alice3:Bobeli2ei3eee"),
            ({}, b"de"),
            ({b"age": 25, b"eyes": b"blue"}, b"d3:agei25e4:eyes4:bluee"),
            ({b"spam.mp3": {b"author": b"Alice", b"length": 100000}}, b"d8:spam.mp3d6:author5:Alice6:lengthi100000eee"),
        )
        for obj, result in testcases:
            self.failUnlessEqual(bencode(obj), result)

    def test_bwrite_stream(self):
        data = BytesIO()
        bwrite(data, {})
        self.failUnlessEqual(data.getvalue(), b"de")

    def test_bwrite_file(self):
        with mockedopen(mode='b') as files:
            bwrite("data", {})
            self.failUnlessEqual(files["data"], b"de")


if __name__ == "__main__":
    unittest.main()
