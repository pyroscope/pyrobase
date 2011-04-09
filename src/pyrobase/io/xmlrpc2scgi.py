""" PyroBase - XMLRPC via SCGI client proxy over various transports.

    Copyright (c) 2011 The PyroScope Project <pyroscope.project@gmail.com>

    Losely based on code Copyright (C) 2005-2007, Glenn Washburn <crass@berlios.de>
    SSH tunneling back-ported from https://github.com/Quantique

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
import time
import socket
import urllib
import urlparse
import xmlrpclib

#
# Helpers to handle SCGI data
# See spec at http://python.ca/scgi/protocol.txt
#
def _encode_netstring(text):
    "Encode text as netstring"
    return "%d:%s," % (len(text), text)


def _encode_headers(headers):
    "Make SCGI from headers (list of tuples)"
    return '\x00'.join(['%s\x00%s' % i for i in headers]) + '\x00'


def _encode_payload(data, headers=None):
    "Wrap data in an scgi request"
    headers = _encode_headers([
        ("CONTENT_LENGTH", str(len(data))),
        ("SCGI", "1"),
    ] + (headers or []))
    
    return _encode_netstring(headers) + data


def _parse_headers(headers):
    """ Get header (key, value) pairs from header string.
    """
    return [line.rstrip().split(": ", 1)
        for line in headers.splitlines()
        if line
    ]


def _parse_response(resp):
    """ Get xmlrpc response from scgi response
    """
    # Assume they care for standards and send us CRLF (not just LF)
    headers, payload = resp.split("\r\n\r\n", 1)
    return payload, _parse_headers(headers)


#
# SCGI request handling
#
class SCGIRequest(object):
    """ Send a SCGI request.
        See spec at "http://python.ca/scgi/protocol.txt".
        
        Use tcp socket
        SCGIRequest('scgi://host:port').send(data)
        
        Or use the named unix domain socket
        SCGIRequest('scgi:///tmp/rtorrent.sock').send(data)
    """

    # Amount of bytes to read at once
    CHUNK_SIZE = 32768

    
    def __init__(self, url):
        self.url = url
        self.resp_headers = []
        self.latency = 0.0

    
    def __send(self, scgireq):
        # Parse endpoint URL
        _, netloc, path, _, _ = urlparse.urlsplit(self.url)
        host, port = urllib.splitport(netloc)
        #~ print '>>>', (netloc, host, port)

        # Connect to the specified endpoint
        start = time.time()
        if netloc:
            addrinfo = list(set(socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)))
            
            assert len(addrinfo) == 1, "There's more than one? %r"%addrinfo
            #~ print addrinfo
            
            sock = socket.socket(*addrinfo[0][:3])
            sock.connect(addrinfo[0][4])
        else:
            # If no host then assume unix domain socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                sock.connect(path)
            except socket.error, exc:
                raise socket.error("Can't connect to %r (%s)" % (path, exc))

        try:
            # Send request        
            sock.send(scgireq)

            # Read response
            resp = []
            while True:
                chunk = sock.recv(self.CHUNK_SIZE)
                if chunk:
                    resp.append(chunk)
                else:
                    break
        finally:
            # Clean up
            sock.close()
            self.latency = time.time() - start
        
        # Return result
        # (note that this returns resp unchanged for lists of length 1 in CPython)
        return ''.join(resp)

    
    def send(self, data):
        """ Send data over scgi to URL and get response.
        """
        scgi_resp = self.__send(_encode_payload(data))
        resp, self.resp_headers = _parse_response(scgi_resp)

        return resp


def scgi_request(url, methodname, deserialize=False, *params):
    """ Send a XMLRPC request over SCGI to the given URL.

        @param url: Endpoint URL.
        @param methodname: XMLRPC method name.
        @param params: tuple of simple python objects.
        @param deserialize: parse XML result? 
        @return: XMLRPC response, or the equivalent Python data.
    """
    xmlreq = xmlrpclib.dumps(params, methodname)
    xmlresp = SCGIRequest(url).send(xmlreq)
    
    if deserialize:
        # This fixes a bug with the Python xmlrpclib module
        # (has no handler for <i8> in some versions)
        xmlresp = xmlresp.replace("<i8>", "<i4>").replace("</i8>", "</i4>")

        # Return deserialized data
        return xmlrpclib.loads(xmlresp)[0][0]
    else:
        # Return raw XML
        return xmlresp


# Types of exceptions thrown
ERRORS = (xmlrpclib.Fault, socket.error)

# Register our schemes to be parsed as having a netloc
urlparse.uses_netloc.append("scgi")
