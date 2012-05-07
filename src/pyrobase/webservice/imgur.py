# -*- coding: utf-8 -*-
# pylint: disable=I0011
""" imgur image hosting.

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
from __future__ import with_statement

import os
import sys
import socket
import hashlib
import httplib
import logging
from contextlib import closing

from pyrobase import parts, pyutil, logutil, fmt
from pyrobase.io import http

json = pyutil.require_json()
LOG = logging.getLogger(__name__)


UploadError = (socket.error, httplib.HTTPException)


class ImgurUploader(object): # pylint: disable=R0903
    """ Upload an image to "imgur.com".

        Sample code::
            imgur = ImgurUploader()
            image = imgur.upload("favicon.jpg")
            # OR: image = imgur.upload(open("favicon.jpg", "rb"))
            # OR: image = imgur.upload(open("favicon.jpg", "rb").read())
            # OR: image = imgur.upload("http://i.imgur.com/5EuUx.jpg")
            print image.links.original
    """
    UPLOAD_URL = "http://api.imgur.com/2/upload.json"


    def __init__(self, api_key=None, mock_http=False):
        """ Initialize upload parameters. 
        
            @param api_key: the API key (optionally taken from IMGUR_APIKEY environment variable).
        """
        self.api_key = api_key or os.environ.get("IMGUR_APIKEY")
        self.mock_http = mock_http


    def upload(self, image, name=None):
        """ Upload the given image, which can be a http[s] URL, a path to an existing file, 
            binary image data, or an open file handle.
        """
        assert self.api_key, "imgur API key is not set! Export the IMGUR_APIKEY environment variable..."

        # Prepare image
        try:
            image_data = (image + '')
        except (TypeError, ValueError):
            assert hasattr(image, "read"), "Image is neither a string nor an open file handle"
            image_type = "file"
            image_data = image
            image_repr = repr(image)
        else:
            if image.startswith("http:") or image.startswith("https:"):
                image_type = "url"
                image_data = image
                image_repr = image
            elif all(ord(i) >= 32 for i in image) and os.path.exists(image):
                image_type = "file"
                image_data = open(image, "rb")
                image_repr = "file:" + image
            else:
                image_type = "base64"
                image_data = image_data.encode(image_type)
                image_repr = "<binary data>"
            
        # See http://api.imgur.com/resources_anon#upload
        fields = [
            ("key",     self.api_key),
            ("type",    image_type),
            ("image",   image_data),
            ("name",    name or hashlib.md5(str(image)).hexdigest()),
        ]
        handle = http.HttpPost(self.UPLOAD_URL, fields, mock_http=self.mock_http)

        response = handle.send()
        if response.status >= 300:
            LOG.warn("Image %s upload failed with result %d %s" % (image_repr, response.status, response.reason))
        else:
            LOG.debug("Image %s uploaded with result %d %s" % (image_repr, response.status, response.reason))
        body = response.read()
        LOG.debug("Response size: %d" % len(body))
        LOG.debug("Response headers:\n  %s" % "\n  ".join([
            "%s: %s" % item for item in response.getheaders()
        ]))

        try:
            result = json.loads(body)
        except (ValueError, TypeError), exc:
            raise httplib.HTTPException("Bad JSON data from imgur upload [%s]: %s" % (exc, logutil.shorten(body)))
        
        if "error" in result: 
            raise httplib.HTTPException("Error response from imgur.com: %(message)s" % result["error"], result)

        return parts.Bunch([(key, parts.Bunch(val))
            for key, val in result["upload"].items()
        ])


def fake_upload_from_url(url):
    """ Return a 'fake' upload data record, so that upload errors 
        can be mitigated by using an original / alternative URL. 
    """
    return parts.Bunch(
        image=parts.Bunch(
            animated='false', bandwidth=0, caption=None, views=0, deletehash=None, hash=None,  
            name=(url.rsplit('/', 1) + [url])[1], title=None, type='image/*', width=0, height=0, size=0,
            datetime=fmt.iso_datetime(), 
        ), 
        links=parts.Bunch(
            delete_page=None, imgur_page=None, 
            original=url, large_thumbnail=url, small_square=url,
        ))


def copy_image_from_url(url, cache_dir=None):
    """ Copy image from given URL and return upload metadata.
    """
    json_path = None
    if cache_dir:
        json_path = os.path.join(cache_dir, "cached-img-%s.json" % hashlib.sha1(url).hexdigest())
        if os.path.exists(json_path):
            LOG.info("Fetching '%s' from cache..." % (url))
            try:
                with closing(open(json_path, "r")) as handle:
                    img_data = json.load(handle)

                return parts.Bunch([(key, parts.Bunch(val))
                    for key, val in img_data.items() # BOGUS pylint: disable=E1103
                ])
            except (EnvironmentError, TypeError, ValueError), exc:
                LOG.warn("Problem reading cached data from '%s', ignoring cache... (%s)" % (json_path, exc))

    LOG.info("Copying '%s'..." % (url))
    img_data = ImgurUploader().upload(url)

    if json_path:
        with closing(open(json_path, "w")) as handle:
            json.dump(img_data, handle)

    return img_data


def _main():
    """ Command line interface for testing.
    """
    import pprint, tempfile

    try:
        image = sys.argv[1]
    except IndexError:
        print("Usage: python -m pyrobase.webservice.imgur <url>")
    else:
        try:
            pprint.pprint(copy_image_from_url(image, cache_dir=tempfile.gettempdir()))
        except UploadError, exc:
            print("Upload error. %s" % exc)


# When called directly, e.g. via
#   python -m pyrobase.webservice.imgur http://i.imgur.com/5EuUx.jpg
if __name__ == "__main__":
    _main()
