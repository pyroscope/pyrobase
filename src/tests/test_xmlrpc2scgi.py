""" PyroBase - SCGI tests.

    List of test cases taken from original BitTorrent code by Bram Cohen.

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
import socket
import urllib2
import logging
import unittest

from pyrobase.io import xmlrpc2scgi

log = logging.getLogger(__name__)
log.trace("module loaded")


class TransportTest(unittest.TestCase):
    
    def test_bad_url(self):
        self.failUnlessRaises(urllib2.URLError, xmlrpc2scgi.transport_from_url, "xxxx:///")

    def test_local_transports(self):
        testcases = (
            ("scgi://localhost:5000/", socket.AF_INET),
            ("localhost:5000", socket.AF_INET),
            ("example.com:5000", socket.AF_INET),
            ("~/tmp/socket", socket.AF_UNIX),
            ("/tmp/socket", socket.AF_UNIX),
            ("scgi:///tmp/socket", socket.AF_UNIX),
            ("scgi:/tmp/socket", socket.AF_UNIX),
        )
        for url, family in testcases:
            result = xmlrpc2scgi.transport_from_url(url) 
            self.failUnlessEqual(result.sock_args[0], family)
            if family == socket.AF_UNIX:
                self.failUnless(result.sock_addr.endswith("/tmp/socket"))


class HelperTest(unittest.TestCase):
    
    def test_encode_netstring(self):
        testcases = (
            ("", "0:,"),
            ("a", "1:a,"),
            #(u"\u20ac", "3:\xe2\x82\xac,"),
        )
        for data, expected in testcases:
            self.failUnlessEqual(xmlrpc2scgi._encode_netstring(data), expected)

    def test_encode_headers(self):
        testcases = (
            ((), ""),
            ((("a", "b"),), "a\0b\0"),
        )
        for data, expected in testcases:
            self.failUnlessEqual(xmlrpc2scgi._encode_headers(data), expected)

    def test_encode_payload(self):
        testcases = (
            ("", "24:%s," % '\0'.join(["CONTENT_LENGTH", "0", "SCGI", "1", ""])),
            ("*"*10, "25:%s," % '\0'.join(["CONTENT_LENGTH", "10", "SCGI", "1", ""]) + "*"*10),
        )
        for data, expected in testcases:
            self.failUnlessEqual(xmlrpc2scgi._encode_payload(data), expected)

    def test_parse_headers(self):
        testcases = (
            ("", {}),
            ("a: b\nc: d\n\n", dict(a="b", c="d")),
        )
        for data, expected in testcases:
            self.failUnlessEqual(xmlrpc2scgi._parse_headers(data), expected)

    def test_parse_response(self):
        data = "Content-Length: 10\r\n\r\n" + "*"*10
        payload, headers = xmlrpc2scgi._parse_response(data)
        self.failUnlessEqual(payload, "*"*10)
        self.failUnlessEqual(headers, {"Content-Length": "10"})


if __name__ == "__main__":
    unittest.main()
