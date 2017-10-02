"""Decode values of the 'DllDirectory' stream.
"""
import textwrap
from enum import Enum
from struct import unpack

import hexdump

from . import storage_parser as sp
from .storage_parser import (StorageContainer, StorageValue, StorageException,
                             StorageType)
from . import utils
from .abc_decoder import AbstractDecoder


class DllEntry(utils.SimpleEqualityMixin):
    def __init__(
            self,
            name: str,
            description: str
    ) -> None:
        self.name = name
        self.description = description

    @classmethod
    def _decode(cls, container: sp.StorageContainer) -> 'DllEntry':
        assert len(container.childs) == 2
        dll_description = DllDescription._decode(container.childs[0])
        dll_name = DllName._decode(container.childs[1])
        inst = cls(name=dll_name.decoded, description=dll_description.decoded)
        return inst

    def __repr__(self):
        class_name = self.__class__.__name__
        format_s = f"[{class_name} {self.name}]"
        desc_s = textwrap.indent(self.description, ' ' * 4)
        return f'\n{format_s}\n{desc_s}\n'


class DllName(
    utils.RawValueMixin,
    utils.UCStringDecodedMixin,
    utils.DecodeBaseMixin,
    utils.SimpleEqualityMixin,
    utils.ReprMixin,
):
    """Name of the dll.
    """
    @classmethod
    def _decode(cls, st_value: sp.StorageValue) -> 'DllName':
        return super()._decode(st_base=st_value)


class DllDescription(
    utils.RawValueMixin,
    utils.UCStringDecodedMixin,
    utils.DecodeBaseMixin,
    utils.SimpleEqualityMixin,
    utils.ReprMixin,
):
    """Description of the dll.
    """
    @classmethod
    def _decode(cls, st_value: sp.StorageValue) -> 'DllDescription':
        return super()._decode(st_base=st_value)


class DllHeader(utils.SimpleEqualityMixin):
    """Header of the DllDirectory stream.
    """

    def __init__(self, value: bytes) -> None:
        self.value = value

    @classmethod
    def _decode(cls, storage_value: sp.StorageValue) -> 'DllHeader':
        inst = cls(
            value=storage_value.value,
        )
        return inst

    def __repr__(self):
        class_name = self.__class__.__name__
        format_s = f"[{class_name}]"
        props = [
            f"hex: {hexdump.dump(self.value)}",
            f"ascii: {utils.bin2ascii(self.value)}",
            f"int: {unpack('i', self.value)[0]}",
        ]
        props_s = '\n'.join(textwrap.indent(str(prop), " " * 4)
                            for prop in props)
        return f"\n{format_s}\n{props_s}\n"


class DllDecoder(AbstractDecoder):
    idn2class_map = {
        0x2037: DllName,
        0x2038: DllEntry,
        0x2039: DllDescription,
        0x21c0: DllHeader,
    }
    #  CONTAINERS = {0x2038}
    NODES = {0x2037, 0x2039, 0x21c0}

    @staticmethod
    def _raise_unknown_id_exc(idn):
        raise StorageException("Unknown Dll storage id: 0x{:x}".format(idn))
