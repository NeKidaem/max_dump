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
        headers[head] = {"count": count}
    return headers

def read_props(bio, headers):
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
    marker = b'\x1e\x00\x00\x00'
    max_fname = sys.argv[1]
    print(max_fname)
    ole = olefile.OleFileIO(max_fname)
    # NOTE: Хранение всего файла в оперативной памяти можно избежать
    # но 3д макс будет крашиться если открыть этот же файл в нем.
    bytes_ = ole.openstream('\x05DocumentSummaryInformation').read()
    ole.close()
    idx = bytes_.index(marker)
    bytes_ = bytes_[idx:]
    bio = io.BytesIO(bytes_)

    marker = b'\x1e\x00\x00\x00'
    headers = get_headers(bio, marker)
    props = read_props(bio, headers)
    out = json.dumps(props, indent=4)
    print(out)


if __name__ == "__main__":
    main()