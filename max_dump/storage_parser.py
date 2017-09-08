"""Extract file properties from 3ds max file.
"""

import io
import json
import sys
from enum import Enum
from struct import unpack
from pprint import pprint

import attr
import hexdump
import olefile

from .utils import INT_S, SHORT_S, read_int


# id + length
HEADER_LENGTH = INT_S + SHORT_S


class StorageType(Enum):
    CONTAINER = "CStorageContainer"
    VALUE = "CStorageValue"

    #  def __repr__(self):
        #  return "{!r}".format(self.value)


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


@attr.s(slots=True)
class Header:
    """Storage header.
    """
    # identifier (unsigned short integer)
    idn = attr.ib()
    length = attr.ib()
    storage_type = attr.ib()


@attr.s(slots=True)
class StorageValue:
    """Storage value.
    """
    header = attr.ib()
    value = attr.ib()


@attr.s(slots=True)
class StorageContainer:
    """Storage container.

    Stores other containers.
    """
    header = attr.ib()
    childs = attr.ib()


def read_idn(stream):
    """Read an identifier of a chunk.

    An identifier is an unsigned short integer.
    """
    return unpack('H', stream.read(SHORT_S))[0]


def read_header(stream):
    """Return id, length, type of the chunk (CStorageContainer or CStorageValue)
    """
    idn = read_idn(stream)
    length = read_int(stream) - HEADER_LENGTH
    # the msb is a flag that helpfully lets us know if the chunk itself
    # contains more chunks, i.e. is a container
    sign_bit = 1 << 31
    if length & sign_bit:
        storage_type = StorageType.CONTAINER
        byte_mask = (1 << 32) - 1
        # unset sign bit and keep length under int size
        length &= ~sign_bit & byte_mask
    else:
        storage_type = StorageType.VALUE
    return Header(idn=idn, length=length, storage_type=storage_type)


def read_value(stream, length):
    val = stream.read(length)
    return hexdump.dump(val)


def read_container(stream, length):
    """Parse the storage stream in the max container file.
    """
    childs = []
    start = stream.tell()
    consumed = 0
    while consumed < length:
        header = read_header(stream)
        child = None
        if header.storage_type == StorageType.CONTAINER:
            nodes = read_container(stream, header.length)
            child = StorageContainer(header, nodes)
        elif header.storage_type == StorageType.VALUE:
            val = read_value(stream, header.length)
            child = StorageValue(header, val)
        else:
            raise Exception(
                "Unknown header type: {}".format(header.storage_type))
        childs.append(child)
        consumed = stream.tell() - start
    return childs


def storage_parse(max_fname, stream_name):
    ole = olefile.OleFileIO(max_fname)
    ba = ole.openstream(stream_name).read()
    ole.close()
    stream = io.BytesIO(ba)
    header = None
    nodes = read_container(stream, len(ba))
    c = StorageContainer(header, nodes)
    return c


def extract_vpq(max_fname):
    return storage_parse(max_fname, 'VideoPostQueue')


def main():
    max_fname = sys.argv[1]
    container = extract_vpq(max_fname)
    #  print(attr.asdict(container))
    print(json.dumps(attr.asdict(container), indent=4, cls=EnumEncoder))


if __name__ == "__main__":
    main()
