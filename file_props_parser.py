"""Extract file properties from 3ds max file.
"""
import io
import json
import sys
from collections import OrderedDict
from struct import unpack

import olefile

from .utils import read_int, INT_S


def read_int(bio):
    return unpack('i', bio.read(INT_S))[0]


def read_str(bio):
    # first read length
    str_len = read_int(bio)
    # then string
    res_str = bio.read(str_len).partition(b'\0')[0]
    return res_str.decode()


def unread(bio, chunk):
    bio.seek(-len(chunk), 1)


def get_headers(bio, marker):
    """An array of headers from contents page.

    Somewhat like MaxScript's
        fileproperties.getPropertyValue #contents 1
    """
    delim = b'\x03\x00\x00\x00'
    headers = OrderedDict()
    while True:
        buf = bio.read(INT_S)
        if not buf == marker:
            unread(bio, buf)
            break
        head = read_str(bio)
        assert delim == bio.read(INT_S)
        count = read_int(bio)
        # `count` is a number of properties that belong to the header.
        headers[head] = {"count": count}
    return headers


def read_props(bio, headers):
    """Read properties for each header.

    Order of headers and `count` are important.
    """
    prop_start = b'\x1e\x10\x00\x00'
    assert prop_start == bio.read(INT_S)
    prop_count = read_int(bio)
    for head in headers:
        items = headers[head]['items'] = []
        count = headers[head]['count']
        i = 0
        while i < count:
            item = read_str(bio)
            items.append(item)
            i += 1
        prop_count -= i
    assert prop_count == 0, ("The actual number of properties does not match "
                             "the one declared")
    return headers


def extract_file_props(max_fname):
    marker = b'\x1e\x00\x00\x00'
    ole = olefile.OleFileIO(max_fname)
    # NOTE: Хранение всего файла в оперативной памяти можно избежать
    # но 3д макс будет крашиться если открыть этот же файл в нем.
    bytes_ = ole.openstream('\x05DocumentSummaryInformation').read()
    ole.close()
    idx = bytes_.index(marker)
    bytes_ = bytes_[idx:]
    bio = io.BytesIO(bytes_)

    headers = get_headers(bio, marker)
    props = read_props(bio, headers)
    return props


def main():
    max_fname = sys.argv[1]
    props = extract_file_props(max_fname)
    out = json.dumps(props, indent=4)
    print(out)


if __name__ == "__main__":
    main()
