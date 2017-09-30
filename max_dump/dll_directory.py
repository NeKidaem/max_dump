"""Decode values of the 'DllDirectory' stream.
"""
import textwrap
from enum import Enum

import hexdump

from .storage_parser import (StorageContainer, StorageValue, StorageException,
                             StorageType)
from . import utils
from .abc_decoder import AbstractDecoder


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

    @property
    def name(self):
        return self.childs[1].name

    @property
    def description(self):
        return self.childs[0].name

    def __repr__(self):
        class_name = self.__class__.__name__
        ext = ("ext" if self.header.extended else "")
        format_s = ("\n[{idn} {name} {count} <{nest}> {ext}]"
                    .format(idn=hex(self.header.idn),
                            name=class_name,
                            count=self.count,
                            nest=self._nest,
                            ext=ext))
        format_s = textwrap.indent(format_s, " " * self._nest * 2)
        childs_s = '\n'.join(textwrap.indent(x, " " * self._nest * 4)
                             for x in [self.name, self.description])
        return '\n'.join([format_s, childs_s])


class DllNodeDecodeMixin:
    @classmethod
    def _decode(cls, storage_value):
        inst = cls(
            name=storage_value.value.decode('utf-16'),
            header=storage_value.header,
            value=storage_value.value,
            nest=storage_value._nest,
        )
        return inst


class DllName(utils.NameValueMixin, StorageValue, DllNodeDecodeMixin):
    """Name of the dll.
    """


class DllDescription(utils.NameValueMixin, StorageValue, DllNodeDecodeMixin):
    """Description of the dll.
    """


class DllHeader(StorageValue):
    """Header of the DllDirectory stream.
    """
    @classmethod
    def _decode(cls, storage_value):
        inst = cls(
            header=storage_value.header,
            value=storage_value.value,
            nest=storage_value._nest,
        )
        return inst


class DllDecoder(AbstractDecoder):
    idn2class_map = {
        0x2037: DllName,
        0x2038: DllEntry,
        0x2039: DllDescription,
        0x21c0: DllHeader,
    }
    CONTAINERS = {0x2038}
    NODES = {0x2037, 0x2039, 0x21c0}

    @staticmethod
    def _raise_unknown_id_exc(idn):
        raise StorageException("Unknown Dll storage id: 0x{:x}".format(idn))
