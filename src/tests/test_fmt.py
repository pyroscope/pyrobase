# pylint: disable=missing-docstring, no-val, expected-use, bad-whitespace
""" Formatting Helper tests.

    Copyright (c) 2011-2020 The PyroScope Project <pyroscope.project@gmail.com>

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

import time
import codecs

import pytest

from pyrobase import fmt


NOW = time.time()


@pytest.mark.parametrize('val, expected', [
    (0,                 "   0 bytes"),
    ("123",             " 123 bytes"),
    (123,               " 123 bytes"),
    (-1,                "-??? bytes"),
    (1023,              "1023 bytes"),
    (1024 ** 1,         "   1.0 KiB"),
    (1024 ** 2,         "   1.0 MiB"),
    (1024 ** 3,         "   1.0 GiB"),
    (1024 ** 4,         "1024.0 GiB"),
    (1024 ** 2 - 51,    "1024.0 KiB"),
    (1024 ** 2 - 52,    "1023.9 KiB"),
    (1024 ** 2 - 512,   "1023.5 KiB"),
    #(, ""),
])
def test_fmt_human_size(val, expected):
    result = fmt.human_size(val)
    assert result == expected


def test_fmt_iso_datetime():
    result = (fmt.iso_datetime(0), fmt.iso_datetime(12*3600), fmt.iso_datetime(23*3600))
    assert any("1970-01-01 " in i for i in result)


def test_fmt_iso_datetime_now():
    result = fmt.iso_datetime()
    assert result.startswith('20')


def test_fmt_iso_datetime_optional_value():
    result = (fmt.iso_datetime(86400), fmt.iso_datetime_optional(86400))
    assert result[0] == result[1]


def test_fmt_iso_datetime_optional_missing():
    result = [fmt.iso_datetime_optional(i) for i in (0, "", None, False)]
    assert all(i == "never" for i in result)


@pytest.mark.parametrize('val, expected', [
    ((NOW,NOW),         "right now"),
    ((NOW,NOW,0,True),  "right now"),
    ((NOW,NOW,1,True),  " now "),
    ((NOW+1,NOW),       "1 sec from now"),
    ((NOW,NOW+1),       "1 sec ago"),
    (("",),             "never"),
    ((None,),           "never"),
    ((0,),              "never"),
    ((0, 0),            "N/A"),
    ((59,0,0,True),     "  59s"),
    ((60,0,0,True),     "   1m"),
    ((3600,0,0,True),   "   1h"),
    ((3601,0,0,True),   "   1h  1s"),
    ((3660,0,0,True),   "   1h  1m"),
    ((3666,0,0,True),   "   1h  1m  6s"),
    ((3666,0,1,True),   "   1h"),
    ((3666,0,2,True),   "   1h  1m"),
    ((3666,0,3,True),   "   1h  1m  6s"),
    ((3666,0,4,True),   "       1h  1m  6s"),
    ((86400,0,0,True),  "   1d"),
    # TODO: lots more
    #(, ""),
])
def test_fmt_human_duration(val, expected):
    result = fmt.human_duration(*val)
    assert result == expected


@pytest.mark.parametrize('val, expected', [
    ("", ""),
    (u"", u""),
    (False, False),
    (None, None),
    (True, "True"),
    (b"\xc3\xaa", u"\xea"),
    (b"\x80", u"\u20ac"),
    (b"\x81", b"\x81"),
    (b"\x8d", b"\x8d"),
    (b"\x8f", b"\x8f"),
    (b"\x90", b"\x90"),
    (b"\x9d", b"\x9d"),
])
def test_fmt_to_unicode(val, expected):
    result = fmt.to_unicode(val)
    assert result == expected


@pytest.mark.parametrize('val, expected', [
    ("", b""),
    (u"", b""),
    (False, False),
    (None, None),
    (u"\xea", b"\xc3\xaa",),
    (b"\x80", b"\xe2\x82\xac"),
    (u"\u20ac", b"\xe2\x82\xac"),
    (b"\xc3\xaa", b"\xc3\xaa"),
    (codecs.BOM_UTF16_LE + b"\1", b"\1"),
    (codecs.BOM_UTF16_BE + b"\1", b"\1"),
    (codecs.BOM_UTF16_LE + b"\x20\x00", b" "),
    (codecs.BOM_UTF16_BE + b"\x00\x20", b" "),
    (codecs.BOM_UTF8 + b"\x20", b" "),
    #(b"\xc3\xc3\x81".decode('cp1252'), "\xc3\xc3\x81"),
])
def test_fmt_to_utf8(val, expected):
    result = fmt.to_utf8(val)
    assert result == expected


@pytest.mark.parametrize('val, expected', [
    ("", b""),
    (u"", b""),
    (u"\xea", b"\xc3\xaa",),
    (u"\u20ac", b"\xe2\x82\xac"),
    (b"\xc3\xaa", b"\xc3\xaa"),
    (b"\xfe\xff\x00\x20", b"\xfe\xff\x00\x20"),
    (b"\xef\xbb\xbf\x20", b"\xef\xbb\xbf\x20"),
    (b"\xc3\xc3\x81", b"\xc3\xc3\x81"),
])
def test_to_console(val, expected):
    result = fmt.to_console(val)
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
