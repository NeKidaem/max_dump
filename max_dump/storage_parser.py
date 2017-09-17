"""Parse chunk based storage.
"""
import io
import os
from enum import Enum, auto
from typing import Iterable

import attr
import olefile

from .utils import SHORT_S, INT_S, LONG_LONG_S
from . import utils


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
    # Length of the value only, no header
    length: int = attr.ib()
    storage_type: StorageType = attr.ib()
    extended: bool = attr.ib(default=False)


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

    _nest: int = attr.ib(init=False, default=0)

    def parse(self, stream_name: str) -> Iterable[StorageContainer]:
        """Parse a chunk-based stream from the max file.

        Interpret bytes from _stream as StorageContainer with childs.
        """
        self._read_stream(stream_name)
        length = self._stream.seek(0, 2)
        self._stream.seek(0, 0)
        items = self._read_container(length)
        return items

    def _read_stream(self, stream_name: str) -> io.BytesIO:
        """Read the stream and save its contents as a stream of bytes.
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

    def _read_container(self, length) -> StorageContainer:
        """Parse the storage stream in the max container file.
        """
        self._nest += 1
        childs = []
        start = stream.tell()
        consumed = 0
        while consumed < length:
            header = self._read_header()

        self._nest -= 1
        return childs

    def _read_header(self) -> StorageHeader:
        """Read id, length, type of the chunk.
        """
        # Number of bytes denoting length of the chunk.
        size_of_length = INT_S
        # Identifier of a chunk.
        idn = utils.read_short(self._stream)
        chunk_length = utils.read_int(self._stream)
        extended = False

        if chunk_length == 0:
            # It is an extended header and needs extra 64 bits.
            extended = True
            size_of_length = LONG_LONG_S
            chunk_length = utils.read_long_long(self._stream)
            assert chunk_length != 0, "Extended length cannot be zero"

        storage_type = None
        # if sign bit is set (length is negative), then the chunk itself
        # contains more chunks, i.e. is a container
        if chunk_length < 0:
            storage_type = StorageType.CONTAINER
            chunk_length = utils.unset_sign_bit(chunk_length, size_of_length)
        else:
            storage_type = StorageType.VALUE

        header_length = SHORT_S + INT_S
        if extended: header_length += LONG_LONG_S

        # We need only the length of the value
        chunk_length -= header_length

        header = StorageHeader(idn, chunk_length, storage_type,
                               extended=extended)
        return header

    def _nest_pad(self) -> str:
        return " " * self._nest * 2





def main():
    header = StorageHeader(1, 1, StorageType.CONTAINER)
    print(header)
    header = StorageHeader(1, 1, StorageType.CONTAINER)
    print(header)


if __name__ == "__main__":
    main()
