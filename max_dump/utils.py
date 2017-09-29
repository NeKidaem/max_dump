# pylint: disable=invalid-name
"""Small functions, objects and constants used by various modules.
"""
import io
import logging
import operator
import string
from typing import Dict, Iterable, Hashable, Union, List
from collections import defaultdict
from struct import unpack, calcsize

SHORT_S = calcsize('h')         # 16
INT_S = calcsize('i')           # 32
LONG_LONG_S = calcsize('q')     # 64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('max_dump')

DictOfDicts = Dict[Hashable, Dict]
DictOfList = Dict[Hashable, List]
DictOrValue = Union[Dict, Hashable]


def read_short(stream: io.BytesIO) -> int:
    """Read signed short integer (usually 16 bit).
    """
    return unpack('h', stream.read(SHORT_S))[0]


def read_int(stream: io.BytesIO) -> int:
    """Read signed integer (usually 32 bit).
    """
    return unpack('i', stream.read(INT_S))[0]


def read_long_long(stream: io.BytesIO) -> int:
    """Read signed integer (usually 64 bit).
    """
    return unpack('q', stream.read(LONG_LONG_S))[0]


def unset_sign_bit(number: int, length: int) -> int:
    """Unset sign bit from a `number'.

    `length' is the size of the number in bytes.
    """
    number_of_bits = length * 8
    # 8bit: 0b1000_0000 = 0x80
    # 32bit: 0x80_00_00_00
    sign_bit = 1 << (number_of_bits - 1)
    # 8bit: 0b1111_1111 = 0xFF
    # 32bit: 0xFF_FF_FF_FF
    byte_mask = (1 << number_of_bits) - 1
    # unset sign bit and keep length under int size
    number &= ~sign_bit & byte_mask
    # 8bit: ~sign_bit = 0b0111_1111
    return number


def _new_key(entry: DictOrValue, key: str) -> Hashable:
    new_key = None
    for sub_key in key.split('__'):
        assert isinstance(entry, Dict)
        new_key = entry[sub_key]
        entry = entry[sub_key]

    assert isinstance(new_key, Hashable)
    return new_key


def index_by(iterable: Iterable[DictOfDicts], key: str) -> DictOfDicts:
    """Return a dictionary from the given iterable.

    `key' may be nested like that: 'header__idn'
    """
    indexed = {}
    for entry in iterable:
        new_key = _new_key(entry, key)
        indexed[new_key] = entry
    return indexed


def group_by(iterable: List[DictOfDicts], key: str) -> DictOfList:
    """Group dictinaries in the iterable by key.
    """
    grouped: DictOfList = defaultdict(list)
    for entry in iterable:
        new_key = _new_key(entry, key)
        grouped[new_key].append(entry)
    return grouped


def bin2ascii(value_bytes):
    s = value_bytes.decode('ascii', 'replace')
    return ''.join(map(lambda x: x if x in string.printable else '.', s))


class CommonEqualityMixin:

    __slots__ = ()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.__slots__ == other.__slots__:
                 attr_getters = [operator.attrgetter(attr) for attr in self.__slots__]
                 return all(getter(self) == getter(other) for getter in attr_getters)

        return False

    def __ne__(self, other):
        return not self.__eq__(other)
