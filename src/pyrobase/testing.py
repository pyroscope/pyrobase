# -*- coding: utf-8 -*-
""" Unittest Helpers.

    Copyright (c) 2009, 2011 The PyroScope Project <pyroscope.project@gmail.com>
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

import errno
from contextlib import contextmanager

try:
    import mock
except ImportError:
    from unittest import mock

from six import PY2, StringIO, BytesIO


class DictItemIO(StringIO):
    """ StringIO that replaces itself in a dict on close.
    """

    def __init__(self, namespace, key, buf=''):
        self.namespace = namespace
        self.key = key

        self.namespace[self.key] = self
        StringIO.__init__(self, buf)


    def close(self):
        self.namespace[self.key] = self.getvalue()
        StringIO.close(self)

class DictItemBytesIO(BytesIO):
    def __init__(self, namespace, key, buf=b''):
        self.namespace = namespace
        self.key = key

        self.namespace[self.key] = self
        BytesIO.__init__(self, buf)


    def close(self):
        self.namespace[self.key] = self.getvalue()
        BytesIO.close(self)


@contextmanager
def mockedopen(fakefiles=None, mode=''):
    """ Mock the open call to use a dict as the file system.

        @param fakefiles: Prepopulated filesystem, this is passed on as the context's target.
    """
    fakefiles = fakefiles or {}

    def mock_open(name, mode=None, buffering=None): # pylint: disable=W0613
        "Helper"
        mode = mode or "r"
        if mode.startswith('r'):
            if name not in fakefiles:
                raise OSError((errno.ENOENT, "File not found", name))
            try:
                fakefiles[name].close()
            except AttributeError:
                pass
            return StringIO(fakefiles[name])
        elif mode.endswith('b'):
            return DictItemBytesIO(fakefiles, name)
        else:
            return DictItemIO(fakefiles, name)

    with mock.patch("__builtin__.open" if PY2 else "builtins.open", mock_open):
        yield fakefiles
