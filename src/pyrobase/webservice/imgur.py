# -*- coding: utf-8 -*-
# pylint: disable=logging-not-lazy, bad-whitespace
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
import time
import socket
import hashlib
import httplib
import logging
from contextlib import closing

try:
    from requests.exceptions import RequestException
    from imgurpython import ImgurClient
except ImportError as _exc:
    raise ImportError("Please 'pip install \"pyrobase[imgur]\"' (%s)" % (_exc,))
from imgurpython.helpers.error import ImgurClientError, ImgurClientRateLimitError

from pyrobase import parts, pyutil, logutil, fmt
from pyrobase.io import http

json = pyutil.require_json()
LOG = logging.getLogger(__name__)

UploadError = (socket.error, httplib.HTTPException, RequestException, ImgurClientError, ImgurClientRateLimitError)

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

    def __init__(self, client_id=None, client_secret=None):
        """ Initialize upload parameters.

            @param client_id: the client ID (optionally taken from IMGUR_CLIENT_ID environment variable).
            @param client_secret: the client secret (optionally taken from IMGUR_CLIENT_SECRET environment variable).
        """
        self.client_id = client_id or os.environ.get("IMGUR_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("IMGUR_CLIENT_SECRET")


    def upload(self, image, name=None):
        """ Upload the given image, which can be a http[s] URL, a path to an existing file,
            binary image data, or an open file handle.
        """
        assert self.client_id, "imgur client ID is not set! Export the IMGUR_CLIENT_ID environment variable..."
        assert self.client_secret, "imgur client secret is not set! Export the IMGUR_CLIENT_SECRET environment variable..."

        # Prepare image
        try:
            image_data = (image + '')
        except (TypeError, ValueError):
            assert hasattr(image, "read"), "Image is neither a string nor an open file handle"
            image_type = "file"
            image_data = image  # XXX are streams supported? need a temp file?
            image_repr = repr(image)
        else:
            if image.startswith("http:") or image.startswith("https:"):
                image_type = "url"
                image_data = image
                image_repr = image
            elif all(ord(i) >= 32 for i in image) and os.path.exists(image):
                image_type = "file"
                image_data = image  # XXX open(image, "rb")
                image_repr = "file:" + image
            else:
                # XXX Not supported anymore (maybe use a temp file?)
                image_type = "base64"
                image_data = image_data.encode(image_type)
                image_repr = "<binary data>"

        # Upload image
        # XXX "name",    name or hashlib.md5(str(image)).hexdigest()),
        client = ImgurClient(self.client_id, self.client_secret)
        result = (client.upload_from_url if image_type == 'url' else client.upload_from_path)(image_data)  # XXX config=None, anon=True)

        if result['link'].startswith('http:'):
            result['link'] = 'https:' + result['link'][5:]
        result['hash'] = result['id']  # compatibility to API v1
        result['caption'] = result['description']  # compatibility to API v1

        return parts.Bunch(
            image=parts.Bunch(result),
            links=parts.Bunch(
                delete_page=None,
                imgur_page=None,
                original=result['link'],
                large_thumbnail="{0}s.{1}".format(*result['link'].rsplit('.', 1)),
                small_square="{0}l.{1}".format(*result['link'].rsplit('.', 1)),
            ))


def fake_upload_from_url(url):
    """ Return a 'fake' upload data record, so that upload errors
        can be mitigated by using an original / alternative URL,
        especially when cross-loading from the web.
    """
    return parts.Bunch(
        image=parts.Bunch(
            animated='false', bandwidth=0, caption=None, views=0, deletehash=None, hash=None,
            name=(url.rsplit('/', 1) + [url])[1], title=None, type='image/*', width=0, height=0, size=0,
            datetime=int(time.time()), # XXX was fmt.iso_datetime() - in API v2 this is a UNIX timestamp
            id='xxxxxxx', link=url, account_id=0, account_url=None, ad_type=0, ad_url='',
            description=None, favorite=False, in_gallery=False, in_most_viral=False,
            is_ad=False, nsfw=None, section=None, tags=[], vote=None,
        ),
        links=parts.Bunch(
            delete_page=None, imgur_page=None,
            original=url, large_thumbnail=url, small_square=url,
        ))


def cache_image_data(cache_dir, cache_key, uploader, *args, **kwargs):
    """ Call uploader and cache its results.
    """
    use_cache = True
    if "use_cache" in kwargs:
        use_cache = kwargs["use_cache"]
        del kwargs["use_cache"]

    json_path = None
    if cache_dir:
        json_path = os.path.join(cache_dir, "cached-img-%s.json" % cache_key)
        if use_cache and os.path.exists(json_path):
            LOG.info("Fetching %r from cache..." % (args,))
            try:
                with closing(open(json_path, "r")) as handle:
                    img_data = json.load(handle)

                return parts.Bunch([(key, parts.Bunch(val))
                    for key, val in img_data.items() # BOGUS pylint: disable=E1103
                ])
            except (EnvironmentError, TypeError, ValueError) as exc:
                LOG.warn("Problem reading cached data from '%s', ignoring cache... (%s)" % (json_path, exc))

    LOG.info("Copying %r..." % (args,))
    img_data = uploader(*args, **kwargs)

    if json_path:
        with closing(open(json_path, "w")) as handle:
            json.dump(img_data, handle)

    return img_data


def copy_image_from_url(url, cache_dir=None, use_cache=True):
    """ Copy image from given URL and return upload metadata.
    """
    return cache_image_data(cache_dir, hashlib.sha1(url).hexdigest(), ImgurUploader().upload, url, use_cache=use_cache)


def _main():
    """ Command line interface for testing.
    """
    import pprint
    import tempfile

    try:
        image = sys.argv[1]
    except IndexError:
        print("Usage: python -m pyrobase.webservice.imgur <url>")
    else:
        try:
            pprint.pprint(copy_image_from_url(image, cache_dir=tempfile.gettempdir()))
        except UploadError as exc:
            print("Upload error. %s" % exc)


# When called directly, e.g. via
#   python -m pyrobase.webservice.imgur http://i.imgur.com/5EuUx.jpg
if __name__ == "__main__":
    _main()
