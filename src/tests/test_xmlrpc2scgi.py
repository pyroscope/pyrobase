""" SCGI tests.

    List of test cases taken from original BitTorrent code by Bram Cohen.

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
import time
import socket
import urllib2
import logging
import unittest

from pyrobase.io import xmlrpc2scgi

log = logging.getLogger(__name__)
log.trace("module loaded")


class MockedTransport(object):

    def __init__(self, url):
        self.url = url

    def send(self, data):
        time.sleep(.01)
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<methodResponse><params>'
            '<param><value><string><![CDATA[%r]]]]></string></value></param>'
            '</params></methodResponse>' % data
        )
        return (
            'Content-Length: %d\r\n'
            '\r\n'
            '%s' % (len(xml), xml)
        )


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
            self.failUnlessEqual("%s[%d]" % (url, result.sock_args[0]),
                                 "%s[%d]" % (url, family))
            if family == socket.AF_UNIX:
                self.failUnless(result.sock_addr.endswith("/tmp/socket"))

    def test_ssh_transports(self):
        testcases = (
            ("scgi+ssh://localhost/tmp/foo",),
            ("scgi+ssh://localhost:5000/~/foo",),
        )
        for url, in testcases:
            # Just make sure they get parsed with no errors
            xmlrpc2scgi.transport_from_url(url)

        # Port handling
        self.failIf("-p" in xmlrpc2scgi.transport_from_url("scgi+ssh://localhost/foo").cmd)
        self.failUnless("-p" in xmlrpc2scgi.transport_from_url("scgi+ssh://localhost:5000/foo").cmd)

        # Errors
        self.failUnlessRaises(urllib2.URLError, xmlrpc2scgi.transport_from_url, "scgi+ssh://localhost:5000")


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


class SCGIRequestTest(unittest.TestCase):

    def test_init(self):
        r1 = xmlrpc2scgi.SCGIRequest("example.com:5000")
        r2 = xmlrpc2scgi.SCGIRequest(r1.transport)
        self.failUnless(r1.transport is r2.transport)

    def test_send(self):
        req = xmlrpc2scgi.SCGIRequest(MockedTransport("foo"))
        resp = req.send("bar")
        bad = "Bad response %r" % resp
        self.failUnless(resp.startswith("<?xml "), bad)
        self.failUnless("bar" in resp, bad)
        self.failIf(req.latency == 0, "Latency cannot be zero")

    def test_scgi_request(self):
        resp = xmlrpc2scgi.scgi_request(MockedTransport("foo"), "bar", "baz")
        bad = "Bad response %s" % resp
        self.failUnless(resp.startswith('"26:CONTENT_LENGTH'), bad)
        self.failUnless("<methodName>bar</methodName>" in resp, bad)
        self.failUnless("<value><string>baz</string></value>" in resp, bad)

    def test_scgi_request_raw(self):
        resp = xmlrpc2scgi.scgi_request(MockedTransport("foo"), "bar", "baz", deserialize=False)
        bad = "Bad response %s" % resp
        self.failUnless(resp.startswith("<?xml version="), bad)
        self.failUnless("<![CDATA[" in resp, bad)


if __name__ == "__main__":
    unittest.main()
