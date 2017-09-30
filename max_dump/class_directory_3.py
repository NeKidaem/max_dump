"""Decode values of the 'ClassDirectory3' stream.
"""
import typing as t
from enum import Enum
from struct import unpack

from . import storage_parser as sp
from . import utils


class ClassDirectoryType(Enum):
    CLASS_ENTRY = 0
    CLASS_HEADER = 1
    CLASS_NAME = 2


class ClassHeader(sp.StorageValue):
    def __init__(
            self,
            dll_index: int,
            class_id: t.Tuple[int, int],
            super_class_id: int,
            *args,
            **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.dll_index = dll_index
        self.class_id = class_id
        self.super_class_id = super_class_id

    @classmethod
    def _decode(cls, st_value: sp.StorageValue) -> 'ClassEntry':
        assert len(st_value.value) == 16, \
            "Length of a class header string must be 16"
        dll_index, *class_id, super_class_id = unpack('4i', st_value.value)
        return cls(dll_index, class_id, super_class_id,
                   header=st_value.header,
                   nest=st_value._nest,
                   value=st_value.value)

    @property
    def _props(self):
        dll_index = f"dll_index: {self.dll_index}"
        class_id_hex = tuple(reversed([hex(x) for x in self.class_id]))
        class_id = f"class_id: {class_id_hex}"
        super_class_id = f"super_class_id: {hex(self.super_class_id)}"
        return [dll_index, class_id, super_class_id]


class ClassName(utils.NameValueMixin, sp.StorageValue):
    @classmethod
    def _decode(cls, st_value: sp.StorageValue) -> 'ClassName':
        return cls(name=st_value.value.decode('utf-16'),
                   header=st_value.header,
                   nest=st_value._nest,
                   value=st_value.value)
