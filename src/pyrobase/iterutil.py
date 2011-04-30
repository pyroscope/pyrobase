# -*- coding: utf-8 -*-
""" Helpers for iterables and collections.

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

def flatten(nested, containers=(list, tuple)):
    """ Flatten a nested list by yielding its scalar items.
    """
    for item in nested:
        if hasattr(item, "next") or isinstance(item, containers):
            for subitem in flatten(item):
                yield subitem
        else:
            yield item
