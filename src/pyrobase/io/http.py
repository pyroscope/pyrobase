# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods
""" HTTP support.

    Copyright (c) 2012 The PyroScope Project <pyroscope.project@gmail.com>
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

import os
import sys
import time
import httplib
import urlparse
import StringIO
import mimetypes

from pyrobase import fmt, parts


class HttpPost(object):
    """ Do a HTTP multipart/form-data POST.
    """

    def __init__(self, url, fields, headers=None, mock_http=False):
        """ Initialize POST data.

            Field values can be strings or files; files
            are expected to have a read() method and SHOULD have a 'name'
            attribute (i.e. look like handles returned by 'open()').

            @param url: the URL to POST to.
            @param fields: sequence of (name, value) tuples.
            @param headers: dict of additional headers.
        """
        self.url = url
        self.fields = fields
        self.headers = headers or {}
        self.mock_http = mock_http


    def __repr__(self):
        """ Show POST data.
        """
        # TODO: headers
        return '\n'.join([
            "POST to '%s' with these fields:" % (self.url,),
        ] + [
            "  %s=%r" % i for i in self.fields
        ])


    def send(self):
        """ Post fields and files to an HTTP server as multipart/form-data.
            Return the server's response.
        """
        scheme, location, path, query, _ = urlparse.urlsplit(self.url)
        assert scheme in ("http", "https"), "Unsupported scheme %r" % scheme

        content_type, body = self._encode_multipart_formdata()
        handle = getattr(httplib, scheme.upper() + "Connection")(location)
        if self.mock_http:
            # Don't actually send anything, print to stdout instead
            handle.sock = parts.Bunch(
                sendall=lambda x: sys.stdout.write(fmt.to_utf8(
                    ''.join((c if 32 <= ord(c) < 127 or ord(c) in (8, 10) else u'\u27ea%02X\u27eb' % ord(c)) for c in x)
                )),
                makefile=lambda dummy, _: StringIO.StringIO("\r\n".join((
                    "HTTP/1.0 204 NO CONTENT",
                    "Content-Length: 0",
                    "",
                ))),
                close=lambda: None,
            )

        handle.putrequest('POST', urlparse.urlunsplit(('', '', path, query, '')))
        handle.putheader('Content-Type', content_type)
        handle.putheader('Content-Length', str(len(body)))
        for key, val in self.headers.items():
            handle.putheader(key, val)
        handle.endheaders()
        handle.send(body)
        #print handle.__dict__

        return handle.getresponse()


    def _encode_multipart_formdata(self):
        """ Encode POST body.
            Return (content_type, body) ready for httplib.HTTP instance
        """
        def get_content_type(filename):
            "Helper to get MIME type."
            return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

        boundary = '----------ThIs_Is_tHe_b0uNdaRY_%d$' % (time.time())
        logical_lines = []
        for name, value in self.fields:
            if value is None:
                continue
            logical_lines.append('--' + boundary)
            if hasattr(value, "read"):
                filename = getattr(value, "name", str(id(value))+".dat")
                logical_lines.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (
                    name,
                    os.path.basename(filename).replace("'", '_').replace('"', '_')
                ))
                logical_lines.append('Content-Type: %s' % get_content_type(filename))
                logical_lines.append('Content-Transfer-Encoding: binary')
                value = value.read()
            else:
                logical_lines.append('Content-Disposition: form-data; name="%s"' % name)
                logical_lines.append('Content-Type: text/plain; charset="UTF-8"')
                value = fmt.to_utf8(value)
            #logical_lines.append('Content-Length: %d' % len(value))
            logical_lines.append('')
            logical_lines.append(value)
        logical_lines.append('--' + boundary + '--')
        logical_lines.append('')

        body = '\r\n'.join(logical_lines)
        content_type = 'multipart/form-data; boundary=%s' % boundary
        return content_type, body
