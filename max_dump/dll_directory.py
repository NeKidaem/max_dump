"""Decode values of the 'DllDirectory' stream.
"""
import textwrap
from enum import Enum

import attr
import hexdump

from .storage_parser import (StorageContainer, StorageValue, StorageException,
                             StorageType)


class DllDirectoryType(Enum):
    DLL_ENTRY = 0  # container type
    DLL_NAME = 1
    DLL_DESCRIPTION = 2


class DllEntry(StorageContainer):
    def __repr__(self):
        class_name = self.__class__.__name__
        ext = ("ext" if self.header.extended else "")
        format_s = ("\n[{} {} {} {} {}]"
                    .format(hex(self.header.idn), class_name,
                            self.header.length, self.count, ext))
        format_s = textwrap.indent(format_s, " " * self._nest * 2)
        childs_s = '\n'.join(repr(c) for c in self.childs)
        return '\n'.join([format_s, childs_s])

    @classmethod
    def decode(cls, container):
        new_childs = []
        for child in container.childs:
            if child.idn == int('0x2037', 16):
                new_child = DllName.decode(child)
            elif child.idn == int('0x2039', 16):
                new_child = DllDescription.decode(child)
            elif child.idn == int('0x2038', 16):
                new_child = DllEntry.decode(child)
            else:
                raise StorageException("Unknown storage id: {}"
                                       .format(child.idn))
            new_childs.append(new_child)
        inst = cls(header=container.header, childs=new_childs)
        return inst


class DllName(StorageValue):
    @classmethod
    def decode(cls, storage_value):
        inst = cls(header=storage_value.header, value=storage_value.value)
        return inst

    @property
    def _props(self):
        props = []
        utf_16 = f"utf-16: {self.value.decode('utf-16')}"
        props.append(utf_16)
        return props


class DllDescription(StorageValue):
    @classmethod
    def decode(cls, storage_value):
        inst = cls(header=storage_value.header, value=storage_value.value)
        return inst

    @property
    def _props(self):
        props = []
        utf_16 = f"utf-16: {self.value.decode('utf-16')}"
        props.append(utf_16)
        return props


class DllHeader(StorageValue):
    @classmethod
    def decode(cls, storage_value):
        inst = cls(header=storage_value.header, value=storage_value.value)
        return inst


@attr.s(slots=True)
class DllDecoder:
    idn2class_map = {
        '0x2037': DllName,
        '0x2038': DllEntry,
        '0x2039': DllDescription,
        '0x21c0': DllHeader,
    }
    @classmethod
    def decode(cls, nodes):
        new_nodes = []
        for node in nodes:
            idn = hex(node.idn)
            if idn not in cls.idn2class_map:
                raise StorageException("Unknown storage id: {:x}"
                        .format(node.idn))
            klass = cls.idn2class_map[hex(node.idn)]
            new_node = klass.decode(node)
            new_nodes.append(new_node)
        return new_nodes
