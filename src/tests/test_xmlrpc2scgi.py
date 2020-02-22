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
    """Transport interface mock."""

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


def test_bad_url():
    with pytest.raises(URLError):
        xmlrpc2scgi.transport_from_url("xxxx:///")

@pytest.mark.parametrize('url, family', [
    ("scgi://localhost:5000/", socket.AF_INET),
    ("localhost:5000", socket.AF_INET),
    ("example.com:5000", socket.AF_INET),
    ("~/tmp/socket", socket.AF_UNIX),
    ("/tmp/socket", socket.AF_UNIX),
    ("scgi:///tmp/socket", socket.AF_UNIX),
    ("scgi:/tmp/socket", socket.AF_UNIX),
])
def test_local_transports(url, family):
    result = xmlrpc2scgi.transport_from_url(url)
    assert "%s[%d]" % (url, result.sock_args[0]) == "%s[%d]" % (url, family)
    if family == socket.AF_UNIX:
        assert result.sock_addr.endswith("/tmp/socket")

@pytest.mark.parametrize('url', [
    "scgi+ssh://localhost/tmp/foo",
    "scgi+ssh://localhost:5000/~/foo",
])
def test_ssh_transports(url):
    # Just make sure they get parsed with no errors
    xmlrpc2scgi.transport_from_url(url)

def test_ssh_url_with_port():
    # Port handling
    assert "-p" not in xmlrpc2scgi.transport_from_url("scgi+ssh://localhost/foo").cmd
    assert "-p" in xmlrpc2scgi.transport_from_url("scgi+ssh://localhost:5000/foo").cmd

def test_ssh_url_error():
    with pytest.raises(URLError):
        xmlrpc2scgi.transport_from_url("scgi+ssh://localhost:5000")


@pytest.mark.parametrize('data, expected', [
    (b"", b"0:,"),
    (b"a", b"1:a,"),
    #(u"\u20ac", "3:\xe2\x82\xac,"),
])
def test_encode_netstring(data, expected):
    assert xmlrpc2scgi._encode_netstring(data) == expected

@pytest.mark.parametrize('data, expected', [
    ((), b""),
    ((("a", "b"),), b"a\0b\0"),
])
def test_encode_headers(data, expected):
    assert xmlrpc2scgi._encode_headers(data) == expected

@pytest.mark.parametrize('data, headers, expected', [
    (b"", None, b"24:%s," % b'\0'.join([b"CONTENT_LENGTH", b"0", b"SCGI", b"1", b""])),
    (b"*"*10, None, b"25:%s," % b'\0'.join([b"CONTENT_LENGTH", b"10", b"SCGI", b"1", b""]) + b"*"*10),
    (
        b"",
        [('a', 'b')],
        b"28:%s," % b'\0'.join([b"CONTENT_LENGTH", b"0", b"SCGI", b"1", b"a", b"b", b""])
    ),
])
def test_encode_payload(data, headers, expected):
    assert xmlrpc2scgi._encode_payload(data, headers=headers) == expected

@pytest.mark.parametrize('data, expected', [
    (b"", {}),
    (b"a: b\nc: d\n\n", dict(a="b", c="d")),
])
def test_parse_headers(data, expected):
    assert xmlrpc2scgi._parse_headers(data) == expected

def test_bad_headers():
    bad_headers = b"a: b\nc; d\n\n"
    with pytest.raises(xmlrpc2scgi.SCGIException):
        xmlrpc2scgi._parse_headers(bad_headers)

def test_parse_response():
    data = b"Content-Length: 10\r\n\r\n" + b"*"*10
    payload, headers = xmlrpc2scgi._parse_response(data)

    assert payload == b"*" * 10
    assert headers == {"Content-Length": "10"}

def test_bad_response():
    bad_data = b"Content-Length: 10\n\n" + b"*"*10
    with pytest.raises(xmlrpc2scgi.SCGIException):
        xmlrpc2scgi._parse_response(bad_data)


def test_scgi_request_init():
    req1 = xmlrpc2scgi.SCGIRequest("example.com:5000")
    req2 = xmlrpc2scgi.SCGIRequest(req1.transport)

    assert req1.transport is req2.transport

def test_scgi_send():
    req = xmlrpc2scgi.SCGIRequest(MockedTransport(b"foo"))
    resp = req.send(b"bar")
    badmsg = "Bad response %r" % resp

    assert resp.startswith(b"<?xml "), badmsg
    assert b"bar" in resp, badmsg
    assert req.latency != 0, "Latency cannot be zero"

def test_scgi_request():
    resp = xmlrpc2scgi.scgi_request(MockedTransport("foo"), "bar", "baz")
    badmsg = "Bad response %s" % resp
    head = '"26:CONTENT_LENGTH' if six.PY2 else 'b"26:CONTENT_LENGTH'

    assert resp.startswith(head), badmsg
    assert "<methodName>bar</methodName>" in resp, badmsg
    assert "<value><string>baz</string></value>" in resp, badmsg

def test_scgi_request_raw():
    resp = xmlrpc2scgi.scgi_request(MockedTransport("foo"), "bar", "baz", deserialize=False)
    badmsg = "Bad response %s" % resp

    assert resp.startswith("<?xml version="), badmsg
    assert "<![CDATA[" in resp, badmsg


if __name__ == "__main__":
    pytest.main([__file__])
