# pylint: disable=missing-docstring, wildcard-import, unused-wildcard-import
# pylint: disable=protected-access, too-few-public-methods
""" Bencode tests.

    List of test cases taken from original BitTorrent code by Bram Cohen.

    Copyright (c) 2009-2020 The PyroScope Project <pyroscope.project@gmail.com>
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

import unittest

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

import pytest

from pyrobase.testing import mockedopen
from pyrobase.bencode import * #@UnusedWildImport


@pytest.mark.parametrize('val', [
    b"",
    b"i",
    b"di1",
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
    b"1",
    b"1:",
    b"9999:x",
    b"l0:",
    b"d0:0:",
    b"d0:",
    b"10:45646",
])
def test_bdecode_errors(val):
    with pytest.raises(BencodeError):
        bdecode(val)

@pytest.mark.parametrize('val, expected', [
    (b"i4e", 4),
    (b"i0e", 0),
    (b"i123456789e", 123456789),
    (b"i-10e", -10),
    (b"0:", ''),
    (b"3:abc", "abc"),
    (b"10:1234567890", "1234567890"),
    (u"10:1234567890", "1234567890"),
    (b"le", []),
    (b"l0:0:0:e", ['', '', '']),
    (b"li1ei2ei3ee", [1, 2, 3]),
    (b"l3:asd2:xye", ["asd", "xy"]),
    (b"ll5:Alice3:Bobeli2ei3eee", [["Alice", "Bob"], [2, 3]]),
    (b"de", {}),
    (b"d3:agei25e4:eyes4:bluee", {"age": 25, "eyes": "blue"}),
    (b"d8:spam.mp3d6:author5:Alice6:lengthi100000eee",
     {"spam.mp3": {"author": "Alice", "length": 100000}}),
])
def test_bdecode_values(val, expected):
    assert bdecode(val) == expected

def test_bdecode_encoding():
    assert bdecode(b"l1:\x801:\x81e", "cp1252") == [u"\u20ac", b"\x81"]

def test_bdecode_bread_stream():
    assert bread(BytesIO(b"de")) == {}

def test_bdecode_bread_file():
    with mockedopen(fakefiles={"empty_dict": "de"}, mode='b'):
        assert bread("empty_dict") == {}


class DunderBencode(object):
    def __init__(self, num):
        self.num = num

    def __bencode__(self):
        return "DunderBencode-{}".format(self.num)

@pytest.mark.parametrize('val', [
    object,
    object(),
    {None: None},
    {object: None},
    {object(): None},
])
def test_bencode_errors(val):
    with pytest.raises(BencodeError):
        bencode(val)

@pytest.mark.parametrize('val, expected', [
    (4, b"i4e"),
    (0, b"i0e"),
    (-10, b"i-10e"),
    (12345678901234567890, b"i12345678901234567890e"),
    (b"", b"0:"),
    (b"abc", b"3:abc"),
    (u"abc", b"3:abc"),
    (b"1234567890", b"10:1234567890"),
    ([], b"le"),
    ([1, 2, 3], b"li1ei2ei3ee"),
    ([[b"Alice", b"Bob"], [2, 3]], b"ll5:Alice3:Bobeli2ei3eee"),
    ({}, b"de"),
    ({b"age": 25, b"eyes": b"blue"}, b"d3:agei25e4:eyes4:bluee"),
    ({u"age": 25, u"eyes": u"blue"}, b"d3:agei25e4:eyes4:bluee"),
    ({1: b"foo"}, b"d1:13:fooe"),
    ({b"spam.mp3": {b"author": b"Alice", b"length": 100000}},
     b"d8:spam.mp3d6:author5:Alice6:lengthi100000eee"),
    ([True, False], b"li1ei0ee"),
    (DunderBencode(2), b"15:DunderBencode-2"),
])
def test_bencode_values(val, expected):
    assert bencode(val) == expected

def test_bencode_bwrite_stream():
    data = BytesIO()
    bwrite(data, {})
    assert  data.getvalue() == b"de"

def test_bencode_bwrite_file():
    with mockedopen(mode='b') as files:
        bwrite("data", {})
        assert files["data"] == b"de"


if __name__ == "__main__":
    pytest.main([__file__])
