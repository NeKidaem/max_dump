"""Decode values of the 'ClassDirectory3' stream.
"""
import textwrap
import typing as t
from enum import Enum
from struct import unpack

from . import storage_parser as sp
from . import dll_directory as dld
from . import utils
from .abc_decoder import AbstractDecoder


class ClassHeader(utils.SimpleEqualityMixin, utils.ReprMixin):
    def __init__(
            self,
            dll_index: int,
            class_id: t.Tuple[int, int],
            super_class_id: int,
    ) -> None:
        self.dll_index = dll_index
        self.class_id = class_id
        self.super_class_id = super_class_id
        self._raw: bytes = None

    @classmethod
    def _decode(cls, st_value: sp.StorageValue) -> 'ClassHeader':
        assert len(st_value.value) == 16, \
            "Length of the class header string must be 16"
        dll_index, *class_id, super_class_id = unpack('4i', st_value.value)
        inst = cls(dll_index, tuple(class_id), super_class_id)
        inst._raw = st_value._raw
        return inst

    @property
    def _props(self):
        dll_index = f"dll_index: {self.dll_index}"
        class_id_hex = tuple(reversed([hex(x) for x in self.class_id]))
        class_id = f"class_id: {class_id_hex}"
        super_class_id = f"super_class_id: {hex(self.super_class_id)}"
        return [dll_index, class_id, super_class_id]


class ClassName(
    utils.RawValueMixin,
    utils.UCStringDecodedMixin,
    utils.DecodeBaseMixin,
    utils.SimpleEqualityMixin,
    utils.ReprMixin,
):
    """Name of the class.
    """
    @classmethod
    def _decode(cls, st_value: sp.StorageValue) -> 'ClassName':
        return super()._decode(st_base=st_value)


class ClassEntry(utils.SimpleEqualityMixin):
    def __init__(
            self,
            header: ClassHeader,
            name: ClassName
    ) -> None:
        self.dll_index = header.dll_index
        self.class_id = header.class_id
        self.super_class_id = header.super_class_id
        self.name = name.decoded
        self._raw: bytes = None

    @classmethod
    def _decode(cls, container: sp.StorageContainer) -> 'ClassEntry':
        assert len(container.childs) == 2
        header = ClassHeader._decode(container.childs[0])
        name = ClassName._decode(container.childs[1])
        inst = cls(header=header, name=name)
        inst._raw = container._raw
        return inst

    def link(self, dll_entries: t.List[dld.DllEntry]) -> 'ClassEntryLinked':
        """Add information about from what dll the class is imported from.
        """
        if len(dll_entries) > 0 and isinstance(dll_entries[0], dld.DllHeader):
            dll_entries.pop(0)

        assert -2 <= self.dll_index < len(dll_entries), 'Invalid DLL entry index'

        if self.dll_index == -1:
            dll_name = 'builtin'
            dll_description = 'Built-in type'
        elif self.dll_index == -2:
            dll_name = 'script'
            dll_description = 'Scripted class'
        else:
            dll_entry = dll_entries[self.dll_index]
            dll_name = dll_entry.name
            dll_description = dll_entry.description

        return ClassEntryLinked(
            name=self.name,
            class_id=self.class_id,
            super_class_id=self.super_class_id,
            dll_name=dll_name,
            dll_description=dll_description,
        )

    @property
    def _props(self):
        dll_index = f"dll_index: {self.dll_index}"
        class_id_hex = tuple(reversed([hex(x) for x in self.class_id]))
        class_id = f"class_id: {class_id_hex}"
        super_class_id = f"super_class_id: {hex(self.super_class_id)}"
        return [dll_index, class_id, super_class_id]

    def __repr__(self):
        class_name = self.__class__.__name__
        format_s = f"[{class_name} {self.name}]"
        props_s = '\n'.join(textwrap.indent(str(prop), " " * 4)
                            for prop in self._props)
        return f"\n{format_s}\n{props_s}\n"


class ClassDecoder(AbstractDecoder):
    idn2class_map = {
        0x2040: ClassEntry,
        0x2042: ClassName,
        0x2060: ClassHeader,
    }
    NODES = {0x2042, 0x2060}

    @staticmethod
    def _raise_unknown_id_exc(idn):
        raise sp.StorageException("Unknown Class storage id: 0x{:x}"
                                  .format(idn))


class ClassEntryLinked:
    def __init__(
            self,
            name: str,
            class_id: t.Tuple[int, int],
            super_class_id: int,
            dll_name: str = '',
            dll_description: str = ''
    ) -> None:
        self.name = name
        self.class_id = class_id
        self.super_class_id = super_class_id
        self.dll_name = dll_name
        self.dll_description = dll_description

    def __repr__(self):
        class_name = self.__class__.__name__
        format_s = f"[{class_name} {self.name}]"
        props = [
                self.dll_name,
                self.dll_description,
                f'class_id: (0x{self.class_id[0]:x}, 0x{self.class_id[1]:x})',
                f'super_class_id: 0x{self.super_class_id:x}',
        ]
        props_s = '\n'.join(textwrap.indent(str(prop), " " * 4)
                            for prop in props)
        return f"{format_s}\n{props_s}\n"
