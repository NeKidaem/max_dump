"""Parse chunk based storage.
"""
import io
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
    def file_exists(self, attribute, value):
        if not os.path.exists(value):
            raise ValueError("File does not exists: {}".format(value))

    _stream: io.BytesIO = attr.ib(init=False, default=None)

    def read_stream(self, stream_name):
        """Read the stream and save its contents as bytes.
        """
        ole = None
        try:
            ole = olefile.OleFileIO(self._max_fname)
            ba = ole.openstream(stream_name).read()
            stream = io.BytesIO(ba)
        except OSError as exc:
            if not ole: raise
            streams = list(zip(*ole.listdir()))[0]
            raise ValueError("Invalid stream name: '{}'. Valid choices are: {}"
                             .format(stream_name, ', '.join(streams))
                            ) from None
        else:
            self._stream = stream
        finally:
            if ole: ole.close()
        return stream


def main():
    header = StorageHeader(1, 1, StorageType.CONTAINER)
    print(header)
    header = StorageHeader(1, 1, StorageType.CONTAINER)
    print(header)


if __name__ == "__main__":
    main()
