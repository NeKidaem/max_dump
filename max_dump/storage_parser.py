# pylint: disable=too-few-public-methods,invalid-name,no-self-use
"""Parse chunk based storage.
"""
import io
import os
import textwrap
from enum import Enum, auto
from struct import unpack
from typing import Iterable, List, Union

import hexdump
import olefile

from .utils import SHORT_S, INT_S, LONG_LONG_S
from . import utils


Storage = Union['StorageContainer', 'StorageValue']


class StorageType(Enum):
    """Type of a storage.
    """
    CONTAINER = auto()
    VALUE = auto()


class StorageException(Exception):
    """Exception, raised when the storage is malformed or of unknown format.
    """


class StorageHeader(utils.CommonEqualityMixin):
    """Storage header.
    """
    __slots__ = ("idn", "length", "storage_type", "extended")

    def __init__(
            self,
            idn: int,
            length: int,
            storage_type: StorageType,
            extended: bool = False
    ) -> None:
        # identifier (unsigned short integer)
        self.idn = idn
        # Length of the value only, no header
        self.length = length
        self.storage_type = storage_type
        self.extended = extended

    def __repr__(self):
        s_t = ("CONTAINER" if self.storage_type == StorageType.CONTAINER
               else "VALUE")
        ext = ("ext" if self.extended else "")
        return ("[{} StorageHeader {} {} {}]"
                .format(hex(self.idn), self.length, s_t, ext))


class StorageBase(utils.CommonEqualityMixin):
    """Storage base class.
    """

    def __init__(
            self,
            header: StorageHeader = None,
            nest: int = 0
    ) -> None:
        self.header = header
        self._nest = nest

    @property
    def idn(self):
        return self.header.idn


class StorageValue(StorageBase):
    """Storage value.
    """
    __slots__ = ("value", )

    def __init__(
            self,
            header: StorageHeader,
            nest: int = 0,
            value: bytes = None
    ) -> None:
        super().__init__(header, nest)
        self.value = value

    @property
    def _props(self):
        props = []
        hex_s = f"hex: {hexdump.dump(self.value)}"
        props.append(textwrap.shorten(hex_s, 80))
        ascii_s = f"ascii: {utils.bin2ascii(self.value)}"
        props.append(ascii_s)
        if len(self.value) == 4:
            int_s, = unpack('i', self.value)
            props.append(f"int: {int_s}")
        return props

    def __repr__(self):
        class_name = self.__class__.__name__
        props = self._props
        body_s = textwrap.indent('\n'.join(props), " " * self._nest + " " * 4)
        ext = ("ext" if self.header.extended else "")
        format_s = ("[{idn} {name} {len} <{nest}> {ext}]"
                    .format(idn=hex(self.header.idn),
                            name=class_name,
                            len=self.header.length,
                            nest=self._nest,
                            ext=ext))
        format_s = textwrap.indent(format_s, " " * self._nest * 2)
        return '\n'.join([format_s, body_s])


class StorageContainer(StorageBase):
    """Storage container.

    Stores other containers.
    """
    __slots__ = ("childs", )

    def __init__(
            self,
            header: StorageHeader = None,
            nest: int = 0,
            childs: Iterable[StorageBase] = None
    ) -> None:
        super().__init__(header, nest)
        if childs is None:
            childs = []
        self.childs = childs

    @property
    def count(self) -> int:
        """Return a number of childs.
        """
        if self.childs is None:
            return 0
        return len(self.childs)

    def __repr__(self):
        class_name = self.__class__.__name__
        ext = ("ext" if self.header.extended else "")
        format_s = ("\n[{idn} {name} {len} {count} <{nest}> {ext}]"
                    .format(idn=hex(self.header.idn),
                            name=class_name,
                            len=self.header.length,
                            count=self.count,
                            nest=self._nest,
                            ext=ext))
        format_s = textwrap.indent(format_s, " " * self._nest * 2)
        childs_s = '\n'.join(repr(c) for c in self.childs)
        return '\n'.join([format_s, childs_s])


class StorageParser:
    """Decoder of the chunk-based streams in the max file.

    Represents chunks as a list of Storage-objects.
    """
    __slots__ = ("_max_fname", "_stream", "_nest")

    def __init__(
            self,
            max_fname: str = None,
    ) -> None:
        max_fname = os.path.abspath(max_fname)
        if not os.path.exists(max_fname):
            raise ValueError("File does not exists: {}".format(max_fname))
        self._max_fname = max_fname

        self._stream: io.BytesIO = None
        self._nest: int = 0

    def parse(self, stream_name: str) -> List[Storage]:
        """Parse a chunk-based stream from the max file.

        Interpret bytes from _stream as list of storages.
        """
        self._read_stream(stream_name)
        length = self._stream.seek(0, 2)
        self._stream.seek(0, 0)
        nodes = self._read_nodes(length)
        return nodes

    def _read_stream(self, stream_name: str) -> io.BytesIO:
        """Read the stream and save its contents as a stream of bytes.
        """
        ole = None
        try:
            ole = olefile.OleFileIO(self._max_fname)
            ba = ole.openstream(stream_name).read()
            stream = io.BytesIO(ba)
        except OSError:
            if not ole:
                raise
            streams = list(zip(*ole.listdir()))[0]
            raise ValueError("Invalid stream name: '{}'. Valid choices are: {}"
                             .format(stream_name, ', '.join(streams))
                             ) from None
        else:
            self._stream = stream
        finally:
            if ole:
                ole.close()
        return stream

    def _read_nodes(self, length) -> List[Storage]:
        """Read items from the storage stream of the max file.
        """
        assert self._stream is not None, "Call _read_stream before"
        self._nest += 1
        items: List[Storage] = []
        start = self._stream.tell()
        consumed = 0
        while consumed < length:
            header = self._read_header()
            if header.storage_type == StorageType.CONTAINER:
                childs = self._read_nodes(header.length)
                st_cont = StorageContainer(header=header, childs=childs)
                st_cont._nest = self._nest
                items.append(st_cont)
            elif header.storage_type == StorageType.VALUE:
                value = self._read_value(header.length)
                st_value = StorageValue(header=header, value=value)
                st_value._nest = self._nest
                items.append(st_value)
            else:
                raise StorageException(
                    "Unknown header type: {}".format(header.storage_type)
                )
            consumed = self._stream.tell() - start

        self._nest -= 1
        return items

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
        if extended:
            header_length += LONG_LONG_S

        # We need only the length of the value
        chunk_length -= header_length

        header = StorageHeader(idn, chunk_length, storage_type,
                               extended=extended)
        return header

    def _read_value(self, length: int) -> bytes:
        return self._stream.read(length)

    def _nest_pad(self) -> str:
        return " " * self._nest * 2


def main():
    """Sort of testing function.
    """
    header = StorageHeader(1, 1, StorageType.CONTAINER)
    print(header)
    header = StorageHeader(1, 1, StorageType.CONTAINER)
    print(header)


if __name__ == "__main__":
    main()
