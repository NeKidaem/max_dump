"""Parse chunk based storage.
"""
import os
import pathlib
from enum import Enum, auto
from typing import Iterable

import attr
import olefile


nest = 0
def pad():
    global nest
    return " " * nest * 2


class StorageType(Enum):
    CONTAINER = auto()
    VALUE = auto()


class StorageException(Exception):
    pass


@attr.s(slots=True)
class StorageHeader:
    """Storage header.
    """
    # identifier (unsigned short integer)
    idn: int = attr.ib()
    length: int = attr.ib()
    storage_type: StorageType = attr.ib()


@attr.s(slots=True)
class StorageBase:
    """Storage base class.
    """
    header: StorageHeader = attr.ib()


@attr.s(slots=True)
class StorageValue(StorageBase):
    """Storage value.
    """
    value: bytes = attr.ib()


@attr.s(slots=True)
class StorageContainer(StorageBase):
    """Storage container.

    Stores other containers.
    """
    childs: Iterable[StorageBase] = attr.ib()
    count: int = attr.ib()


@attr.s(slots=True)
class StorageParser:
    _max_fname: str = attr.ib(convert=os.path.abspath)

    @_max_fname.validator
    def valid_max_file(self, attribute, value):
        self._ole = olefile.OleFileIO(value)

    _stream_name: str = attr.ib()

    @_stream_name.validator
    def stream_exists(self, attribute, value):
        try:
            self._stream = self._ole.openstream(value)
        except OSError as exc:
            streams = list(zip(*self._ole.listdir()))[0]
            raise ValueError("Invalid stream name: '{}'. Valid choices are: {}"
                             .format(value, ', '.join(streams))) from None

    _stream: str = attr.ib(init=False, default=None)
    _ole: olefile.OleFileIO = attr.ib(init=False, default=None)


def main():
    header = StorageHeader(1, 1, StorageType.CONTAINER)
    print(header)
    header = StorageHeader(1, 1, StorageType.CONTAINER)
    print(header)


if __name__ == "__main__":
    main()
