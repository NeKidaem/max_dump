"""Extract file properties from 3ds max file.
"""

import io
import json
import sys
from enum import IntEnum, unique, auto
from struct import unpack
from pprint import pprint

import attr
import hexdump
import olefile

from .utils import INT_S, SHORT_S, read_int


# id + length
HEADER_LENGTH = INT_S + SHORT_S


DEBUG = False
#  DEBUG = True

def print(*args, **kwargs):
    if DEBUG:
        __builtins__['print'](*args, **kwargs)


@unique
class StorageType(IntEnum):
    # Container types 100-199
    CONTAINER = 100
    DLL_ENTRY = auto()
    # Value types 200-299
    VALUE = 200
    DLL_DESCRIPTION = auto()
    DLL_NAME = auto()

    def is_value(self):
        return self.VALUE <= self

    def is_container(self):
        return self.CONTAINER <= self < self.VALUE

    def __repr__(self):
        return self.name


def utf_16_decode(val):
    return bytes.decode(val, 'utf-16')


KNOWN_TYPES = {
    "0x2037": {
        "storage_type": StorageType.DLL_NAME,
        "decoder": utf_16_decode,
    },
    "0x2038": {
        "storage_type": StorageType.DLL_ENTRY,
        "decoder": lambda _: None,
    },
    "0x2039": {
        "storage_type": StorageType.DLL_DESCRIPTION,
        "decoder": utf_16_decode,
    },
}


@attr.s(slots=True)
class Header:
    """Storage header.
    """
    # identifier (unsigned short integer)
    idn = attr.ib()
    length = attr.ib()
    storage_type = attr.ib()
    storage_type_name = attr.ib()


@attr.s(slots=True)
class StorageValue:
    """Storage value.
    """
    header = attr.ib()
    value = attr.ib()
    parsed = attr.ib()

    @property
    def value_bytes(self):
        return bytes.fromhex(self.value)

    @parsed.default
    def parsed_default(self):
        if self.header.idn not in KNOWN_TYPES:
            return None
        idn = self.header.idn
        decoder = KNOWN_TYPES[idn]["decoder"]
        return decoder(self.value_bytes)


@attr.s(slots=True)
class StorageContainer:
    """Storage container.

    Stores other containers.
    """
    header = attr.ib()
    childs = attr.ib()
    count = attr.ib()

    @count.default
    def count_default(self):
        return len(self.childs)


class StorageException(Exception):
    pass


nest = 0

def pad():
    global nest
    return " " * nest * 2


def read_idn(stream) -> hex:
    """Read an identifier of a chunk.

    An identifier is an unsigned short integer.
    """
    b = stream.read(SHORT_S)
    print(pad(), hexdump.dump(b))
    return hex(unpack('H', b)[0])


def read_int(stream):
    b = stream.read(INT_S)
    print(pad(), hexdump.dump(b))
    return unpack('i', b)[0]
    #  return unpack('i', stream.read(INT_S))[0]


def read_header(stream):
    """Return id, length, type of the chunk.
    """
    idn = read_idn(stream)
    length = read_int(stream)
    if length == 0:
        raise StorageException(
                "Extended header length is not yet supported: {}".format(idn)
        )
    length -= HEADER_LENGTH
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
    # Specify type if `idn' is known.
    if idn in KNOWN_TYPES:
        storage_type = KNOWN_TYPES[idn]["storage_type"]
    return Header(idn, length, storage_type, storage_type.name)


def read_value(stream, length):
    val = stream.read(length)
    s = val.hex()
    print(pad(), s)
    return s


def read_container(stream, length):
    """Parse the storage stream in the max container file.
    """
    global nest
    nest += 1
    childs = []
    start = stream.tell()
    consumed = 0
    while consumed < length:
        header = read_header(stream)
        child = None
        print(pad(), header.storage_type_name)
        if header.storage_type.is_container():
        #  if header.storage_type == StorageType.CONTAINER:
            print(pad(), "container")
            nodes = read_container(stream, header.length)
            child = StorageContainer(header, nodes)
        #  elif header.storage_type == StorageType.VALUE:
        elif header.storage_type.is_value():
            print(pad(), "value")
            val = read_value(stream, header.length)
            child = StorageValue(header, val)
        else:
            raise Exception(
                "Unknown header type: {}".format(header.storage_type)
            )
        childs.append(attr.asdict(child))
        consumed = stream.tell() - start
    nest -= 1
    return childs


def read_stream(max_fname, stream_name):
    """Read the stream and return its contents as bytes.
    """
    ole = olefile.OleFileIO(max_fname)
    ba = ole.openstream(stream_name).read()
    ole.close()
    return ba


def storage_parse(max_fname, stream_name):
    ba = read_stream(max_fname, stream_name)
    stream = io.BytesIO(ba)
    nodes = read_container(stream, len(ba))
    return nodes


def extract_vpq(max_fname):
    return storage_parse(max_fname, 'VideoPostQueue')


def main():
    max_fname = sys.argv[1]
    container = extract_vpq(max_fname)
    #  print(attr.asdict(container))
    print(json.dumps(container, indent=4, cls=EnumEncoder, sort_keys=True))


if __name__ == "__main__":
    main()
