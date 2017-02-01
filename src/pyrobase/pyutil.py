# -*- coding: utf-8 -*-
# pylint: disable=
""" Python Language / Runtime Support.

    Copyright (c) 2011-2017 The PyroScope Project <pyroscope.project@gmail.com>
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
import logging

LOG = logging.getLogger(__name__)


def require_json():
    """ Load the best available json library on demand.
    """
    # Fails when "json" is missing and "simplejson" is not installed either
    try:
        import json # pylint: disable=F0401
        return json
    except ImportError:
        try:
            import simplejson # pylint: disable=F0401
            return simplejson
        except ImportError, exc:
            raise ImportError("""Please 'pip install "simplejson>=2.1.6"' (%s)""" % (exc,))
