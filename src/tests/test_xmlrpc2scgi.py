# pylint: disable=missing-docstring, too-few-public-methods
# pylint: disable=protected-access
""" SCGI tests.

    List of test cases taken from original BitTorrent code by Bram Cohen.

    Copyright (c) 2011-2020 The PyroScope Project <pyroscope.project@gmail.com>
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
from __future__ import absolute_import, print_function, unicode_literals

import time
import socket
import unittest

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError

import six
import pytest

from pyrobase.io import xmlrpc2scgi


class MockedTransport(object):

    def __init__(self, url):
        self.url = url

    def send(self, data):
        time.sleep(.01)
        xml = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<methodResponse><params>'
            b'<param><value><string><![CDATA[%r]]></string></value></param>'
            b'</params></methodResponse>' % data
        )
        return (
            b'Content-Length: %d\r\n' % len(xml),
            b'\r\n',
            b'%s' % xml
        )


class TransportTest(unittest.TestCase):

    def test_bad_url(self):
        self.assertRaises(URLError, xmlrpc2scgi.transport_from_url, "xxxx:///")

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
            self.assertEqual("%s[%d]" % (url, result.sock_args[0]),
                             "%s[%d]" % (url, family))
            if family == socket.AF_UNIX:
                self.assertTrue(result.sock_addr.endswith("/tmp/socket"))

    def test_ssh_transports(self):
        testcases = (
            ("scgi+ssh://localhost/tmp/foo",),
            ("scgi+ssh://localhost:5000/~/foo",),
        )
        for url, in testcases:
            # Just make sure they get parsed with no errors
            xmlrpc2scgi.transport_from_url(url)

        # Port handling
        self.assertFalse("-p" in xmlrpc2scgi.transport_from_url("scgi+ssh://localhost/foo").cmd)
        self.assertTrue("-p" in xmlrpc2scgi.transport_from_url("scgi+ssh://localhost:5000/foo").cmd)

        # Errors
        self.assertRaises(URLError, xmlrpc2scgi.transport_from_url, "scgi+ssh://localhost:5000")


class HelperTest(unittest.TestCase):

    def test_encode_netstring(self):
        testcases = (
            (b"", b"0:,"),
            (b"a", b"1:a,"),
            #(u"\u20ac", "3:\xe2\x82\xac,"),
        )
        for data, expected in testcases:
            self.assertEqual(xmlrpc2scgi._encode_netstring(data), expected)

    def test_encode_headers(self):
        testcases = (
            ((), b""),
            ((("a", "b"),), b"a\0b\0"),
        )
        for data, expected in testcases:
            self.assertEqual(xmlrpc2scgi._encode_headers(data), expected)

    def test_encode_payload(self):
        testcases = (
            (b"", None, b"24:%s," % b'\0'.join([b"CONTENT_LENGTH", b"0", b"SCGI", b"1", b""])),
            (b"*"*10, None, b"25:%s," % b'\0'.join([b"CONTENT_LENGTH", b"10", b"SCGI", b"1", b""]) + b"*"*10),
            (
                b"",
                [('a', 'b')],
                b"28:%s," % b'\0'.join([b"CONTENT_LENGTH", b"0", b"SCGI", b"1", b"a", b"b", b""])
            ),
        )
        for data, headers, expected in testcases:
            self.assertEqual(xmlrpc2scgi._encode_payload(data, headers=headers), expected)

    def test_parse_headers(self):
        testcases = (
            (b"", {}),
            (b"a: b\nc: d\n\n", dict(a="b", c="d")),
        )
        for data, expected in testcases:
            self.assertEqual(xmlrpc2scgi._parse_headers(data), expected)

        bad_headers = b"a: b\nc; d\n\n"
        self.assertRaises(xmlrpc2scgi.SCGIException, xmlrpc2scgi._parse_headers, bad_headers)

    def test_parse_response(self):
        data = b"Content-Length: 10\r\n\r\n" + b"*"*10
        payload, headers = xmlrpc2scgi._parse_response(data)
        self.assertEqual(payload, b"*"*10)
        self.assertEqual(headers, {"Content-Length": "10"})

        bad_data = b"Content-Length: 10\n\n" + b"*"*10
        self.assertRaises(xmlrpc2scgi.SCGIException, xmlrpc2scgi._parse_response, bad_data)


class SCGIRequestTest(unittest.TestCase):

    def test_init(self):
        req1 = xmlrpc2scgi.SCGIRequest("example.com:5000")
        req2 = xmlrpc2scgi.SCGIRequest(req1.transport)
        self.assertTrue(req1.transport is req2.transport)

    def test_send(self):
        req = xmlrpc2scgi.SCGIRequest(MockedTransport(b"foo"))
        resp = req.send(b"bar")
        bad = "Bad response %r" % resp
        self.assertTrue(resp.startswith(b"<?xml "), bad)
        self.assertTrue(b"bar" in resp, bad)
        self.assertFalse(req.latency == 0, "Latency cannot be zero")

    def test_scgi_request(self):
        resp = xmlrpc2scgi.scgi_request(MockedTransport("foo"), "bar", "baz")
        bad = "Bad response %s" % resp
        if six.PY2:
            self.assertTrue(resp.startswith('"26:CONTENT_LENGTH'), bad)
        else:
            self.assertTrue(resp.startswith('b"26:CONTENT_LENGTH'), bad)
        self.assertTrue("<methodName>bar</methodName>" in resp, bad)
        self.assertTrue("<value><string>baz</string></value>" in resp, bad)

    def test_scgi_request_raw(self):
        resp = xmlrpc2scgi.scgi_request(MockedTransport("foo"), "bar", "baz", deserialize=False)
        bad = "Bad response %s" % resp
        self.assertTrue(resp.startswith("<?xml version="), bad)
        self.assertTrue("<![CDATA[" in resp, bad)


if __name__ == "__main__":
    pytest.main([__file__])
