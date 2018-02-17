# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods,invalid-name
""" Bencode support.

    Copyright (c) 2009-2017 The PyroScope Project <pyroscope.project@gmail.com>

    See http://en.wikipedia.org/wiki/Bencode
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

from six import string_types, text_type, binary_type, integer_types


class BencodeError(ValueError):
    """ Error during decoding or encoding.
    """


class Decoder(object):
    """ Decode a string or stream to an object.
    """

    def __init__(self, data, char_encoding='utf-8'):
        """ Initialize encoder.
        """
        if isinstance(data, text_type):
            self.data = data.encode(char_encoding)
        else:
            self.data = data
        self.offset = 0
        self.char_encoding = char_encoding


    def decode(self, check_trailer=False): # pylint: disable=I0011,R0912
        """ Decode data in C{self.data} and return deserialized object.

            @param check_trailer: Raise error if trailing junk is found in data?
            @raise BencodeError: Invalid data.
        """
        try:
            kind = self.data[self.offset:self.offset+1]
        except (IndexError):
            raise BencodeError("Unexpected end of data at offset %d/%d" % (
                self.offset, len(self.data),

            ))

        if b'0' <= kind <= b'9':
            # String
            try:
                end = self.data.find(b':', self.offset)
                length = int(self.data[self.offset:end], 10)
            except (ValueError, TypeError):
                raise BencodeError("Bad string length at offset %d (%r...)" % (
                    self.offset, self.data[self.offset:self.offset+32]
                ))

            self.offset = end+length+1
            obj = self.data[end+1:self.offset]

            if self.char_encoding:
                try:
                    obj = obj.decode(self.char_encoding)
                except (UnicodeError, AttributeError):
                    # deliver non-decodable string (byte arrays) as-is
                    pass
        elif kind == b'i':
            # Integer
            try:
                end = self.data.find(b'e', self.offset+1)
                obj = int(self.data[self.offset+1:end], 10)
            except (ValueError, TypeError):
                raise BencodeError("Bad integer at offset %d (%r...)" % (
                    self.offset, self.data[self.offset:self.offset+32]
                ))
            self.offset = end+1
        elif kind == b'l':
            # List
            self.offset += 1
            obj = []
            while self.data[self.offset:self.offset+1] != b'e':
                obj.append(self.decode())
            self.offset += 1
        elif kind == b'd':
            # Dict
            self.offset += 1
            obj = {}
            while self.data[self.offset:self.offset+1] != b'e':
                key = self.decode()
                obj[key] = self.decode()
            self.offset += 1
        else:
            raise BencodeError("Format error at offset %d (%r...)" % (
                self.offset, self.data[self.offset:self.offset+32]
            ))

        if check_trailer and self.offset != len(self.data):
            raise BencodeError("Trailing data at offset %d (%r...)" % (
                self.offset, self.data[self.offset:self.offset+32]
            ))

        return obj



class Encoder(object):
    """ Encode a given object to an array of bytestrings.
    """

    def __init__(self, char_encoding='utf-8'):
        """ Initialize encoder.
        """
        self.result = []
        self.char_encoding = char_encoding

    def encode(self, obj):
        """ Add the given object to the result.
        """
        if isinstance(obj, bool):
            if obj:
                self.result.extend([b"i1e"])
            else:
                self.result.extend([b"i0e"])
        elif isinstance(obj, integer_types):
            self.result.extend([b"i", text_type(obj).encode('utf-8'), b"e"])
        elif isinstance(obj, string_types):
            if isinstance(obj, text_type):
                obj = obj.encode(self.char_encoding)
            self.result.extend([str(len(obj)).encode(self.char_encoding), b':', obj])
        elif isinstance(obj, binary_type):
            # Previous check catches py2's str
            self.result.extend([str(len(obj)).encode(self.char_encoding), b':', obj])
        elif hasattr(obj, "__bencode__"):
            self.encode(obj.__bencode__())
        elif hasattr(obj, "items"):
            # Dictionary
            self.result.append(b'd')
            for key, val in sorted(obj.items()):
                if not isinstance(key, string_types + (binary_type,)):
                    raise BencodeError("Dict key must be bytestring, found '%s'" % key)
                if isinstance(key, text_type):
                    key = key.encode(self.char_encoding)
                self.result.extend([str(len(key)).encode(self.char_encoding), b':', key])
                self.encode(val)
            self.result.append(b'e')
        else:
            # Treat as iterable
            try:
                items = iter(obj)
            except TypeError as exc:
                raise BencodeError("Unsupported non-iterable object %r of type %s (%s)" % (
                    obj, type(obj), exc
                ))
            else:
                self.result.append(b'l')
                for item in items:
                    self.encode(item)
                self.result.append(b'e')

        return self.result


def bdecode(data, char_encoding='utf-8'):
    """ Decode a string or stream to an object.
    """
    return Decoder(data, char_encoding).decode(check_trailer=True)


def bencode(obj, char_encoding='utf-8'):
    """ Encode a given object to data.
    """
    return b''.join(Encoder(char_encoding).encode(obj))


def bread(stream):
    """ Decode a file or stream to an object.
    """
    if hasattr(stream, "read"):
        return bdecode(stream.read())
    else:
        handle = open(stream, "rb")
        try:
            return bdecode(handle.read())
        finally:
            handle.close()


def bwrite(stream, obj):
    """ Encode a given object to a file or data.
    """
    handle = None
    if not hasattr(stream, "write"):
        stream = handle = open(stream, "wb")
    try:
        stream.write(bencode(obj))
    finally:
        if handle:
            handle.close()
