"""Small functions, objects and constants used by various modules.
"""
import logging
from collections import defaultdict
from struct import unpack, calcsize

SHORT_S = calcsize('h')         # 16
INT_S = calcsize('i')           # 32
LONG_LONG_S = calcsize('q')     # 64

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('max_dump')


def read_short(stream):
    """Read signed short integer (usually 16 bit).
    """
    return unpack('h', stream.read(SHORT_S))[0]


def read_int(stream):
    """Read signed integer (usually 32 bit).
    """
    return unpack('i', stream.read(INT_S))[0]


def read_long_long(stream):
    """Read signed integer (usually 64 bit).
    """
    return unpack('q', stream.read(LONG_LONG_S))[0]


def unset_sign_bit(number, length):
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


def _new_key(entry, key):
    new_key = entry
    for sub_key in key.split('__'):
        new_key = new_key[sub_key]
    return new_key


def index_by(iterable, key):
    """Return a dictionary from the given iterable.

    `key' may be nested like that: 'header__idn'
    """
    indexed = {}
    for entry in iterable:
        new_key = _new_key(entry, key)
        indexed[new_key] = entry
    return indexed


def group_by(iterable, key):
    """Group dictinaries in the iterable by key.
    """
    grouped = defaultdict(list)
    for entry in iterable:
        new_key = _new_key(entry, key)
        grouped[new_key].append(entry)
    return grouped
