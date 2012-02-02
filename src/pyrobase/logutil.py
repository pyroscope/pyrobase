""" Logging Support.

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

# Maximum length of object representations
MAX_DISPLAY_LEN = 99


def shorten(text):
    """ Reduce text length for displaying / logging purposes.
    """
    if len(text) >= MAX_DISPLAY_LEN:
        text = text[:MAX_DISPLAY_LEN//2]+"..."+text[-MAX_DISPLAY_LEN//2:]
    return text

