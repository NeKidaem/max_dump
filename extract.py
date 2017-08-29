"""Read file properties from 3ds Max file.

More about properties here
http://help.autodesk.com/view/3DSMAX/2016/ENU/?guid=__files_GUID_A8663B8E_7E30_474E_B3DB_E21585F125B1_htm

Notes on the structure of the stream '\x05DocumentSummaryInformation'
===================

1E 00 00 00 -- Header delimiter
08 00 00 00 -- String length
General
00          -- Null terminator and padding
03 00 00 00 -- Some value, may be delimiter
04 00 00 00 -- Number of properties under the header

1E 00 00 00
0C 00 00 00
Mesh 20 Totals
00
03 00 00 00
02 00 00 00

==================
List of properties begins right after the last header.
==================

1E 10 00 00 -- Marks the begining of the list
36 00 00 00 -- magic value
18 00 00 00 -- string length
3ds Max Version: 18.00
00 00       -- null terminator, padded

10 00 00 00 -- string length
Uncompressed
00 00 00 00

14 00 00 00
Build: 18.0.873.0
00 00 00

18 00 00 00
Saved As Version: 18.00
00
10 00 00 00

Vertices: 507
00 00 00
0C 00 00 00
Faces: 992

....

14 00 00 00
RenderElements=0
00 00 00 00

34 00 00 00
03 00 00 00
"""
import io
import json
import sys
from collections import OrderedDict
from struct import unpack, pack

import olefile
from hexdump import hexdump


INT_S = 4


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
    DELIM = b'\x03\x00\x00\x00'
    headers = OrderedDict()
    while True:
        buf = bio.read(INT_S)
        if not buf == marker:
            unread(bio, buf)
            break
        head = read_str(bio)
        assert DELIM == bio.read(INT_S)
        count = read_int(bio)
        # `count` is a number of properties that belong to the header.
        headers[head] = {"count": count}
    return headers


def read_props(bio, headers):
    """Read properties for each header.

    Order of headers and `count` are important.
    """
    PROP_START = b'\x1e\x10\x00\x00'
    assert PROP_START == bio.read(INT_S)
    some_val = bio.read(INT_S)  # idk what it is
    for head in headers:
        items = headers[head]['items'] = []
        count = headers[head]['count']
        i = 0
        while i < count:
            item = read_str(bio)
            items.append(item)
            i += 1
    return headers


def main():
    MARKER = b'\x1e\x00\x00\x00'
    max_fname = sys.argv[1]
    print(max_fname)
    ole = olefile.OleFileIO(max_fname)
    # NOTE: Хранение всего файла в оперативной памяти можно избежать
    # но 3д макс будет крашиться если открыть этот же файл в нем.
    bytes_ = ole.openstream('\x05DocumentSummaryInformation').read()
    ole.close()
    idx = bytes_.index(MARKER)
    bytes_ = bytes_[idx:]
    bio = io.BytesIO(bytes_)

    headers = get_headers(bio, MARKER)
    props = read_props(bio, headers)
    out = json.dumps(props, indent=4)
    print(out)


if __name__ == "__main__":
    main()