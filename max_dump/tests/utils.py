import io

import max_dump.storage_parser as sp


def one_storage_from_ba_hex(ba_hex, valid_max_fname, debug=False):
    ba = bytes.fromhex(ba_hex)
    parser = sp.StorageParser(valid_max_fname)
    parser._stream = io.BytesIO(ba)
    parser._debug = debug
    return parser._read_one_storage()

def all_storages_from_ba_hex(ba_hex, valid_max_fname, debug=False):
    ba = bytes.fromhex(ba_hex)
    parser = sp.StorageParser(valid_max_fname)
    parser._stream = io.BytesIO(ba)
    parser._debug = debug
    return parser.read_storages(len(ba))
