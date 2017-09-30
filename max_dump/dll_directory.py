"""Decode values of the 'DllDirectory' stream.
"""
import textwrap
from enum import Enum

import hexdump

from .storage_parser import (StorageContainer, StorageValue, StorageException,
                             StorageType)


class DllDirectoryType(Enum):
    DLL_ENTRY = 0  # container type
    DLL_NAME = 1
    DLL_DESCRIPTION = 2


class DllEntry(StorageContainer):

    @classmethod
    def _decode(cls, container):
        new_childs = []
        inst = cls(header=container.header, childs=new_childs)
        inst._nest = container._nest
        return inst


class DllNodeDecodeMixin:
    @classmethod
    def _decode(cls, storage_value):
        inst = cls(header=storage_value.header, value=storage_value.value)
        inst._nest = storage_value._nest
        return inst


class DllNodePropsMixin:
    @property
    def _props(self):
        props = []
        utf_16 = f"utf-16: {self.value.decode('utf-16')}"
        props.append(utf_16)
        return props


class DllName(DllNodePropsMixin, StorageValue, DllNodeDecodeMixin):
    """Name of the dll.
    """

class DllDescription(DllNodePropsMixin, StorageValue, DllNodeDecodeMixin):
    """Description of the dll.
    """


class DllHeader(StorageValue, DllNodeDecodeMixin):
    """Header of the DllDirectory stream.
    """


class DllDecoder:
    idn2class_map = {
        '0x2037': DllName,
        '0x2038': DllEntry,
        '0x2039': DllDescription,
        '0x21c0': DllHeader,
    }
    CONTAINERS = {'0x2038'}
    NODES = {'0x2037', '0x2039', '0x21c0'}

    @classmethod
    def decode(cls, nodes):
        return cls._decode_many(nodes)

    @classmethod
    def _decode_one(cls, node):
        idn = hex(node.idn)
        if idn not in cls.idn2class_map:
            raise StorageException("Unknown storage id: 0x{:x}".format(node.idn))

        klass = cls.idn2class_map[idn]
        decoded_node = klass._decode(node)

        if idn in cls.CONTAINERS:
            decoded_node.childs = cls._decode_many(node.childs)

        return decoded_node

    @classmethod
    def _decode_many(cls, nodes):
        return [cls._decode_one(node) for node in nodes]
