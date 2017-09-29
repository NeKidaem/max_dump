"""Unit tests for dll_directory.
"""
import unittest
import pathlib

import max_dump.storage_parser as sp
import max_dump.dll_directory as dld
from . import utils


BASE_DIR = pathlib.Path(__file__).parent


class DllDecoderTests(unittest.TestCase):
    def setUp(self):
        self.valid_max_fname = BASE_DIR / "./data/01-teapot_no_cams_vray.max"

    def test_decode_one_dll_header(self):
        ba_hex = (
            'C0 21 '
            '0A 00 00 00 '
            '   69 03 50 46'
        )
        st_value = utils.one_storage_from_ba_hex(ba_hex, self.valid_max_fname)
        dll_header = dld.DllDecoder._decode_one(st_value)
        dll_header_ref = dld.DllHeader._decode(st_value)
        self.assertEqual(dll_header, dll_header_ref)

    def test_decode_one_dll_name(self):
        ba_hex = (
            '37 20 '
            '18 00 00 00 '
            '    62 00 69 00 70 00 65 00 64 00 2E 00 64 00 6C 00 63 00'
        )
        st_value = utils.one_storage_from_ba_hex(ba_hex, self.valid_max_fname)
        dll_name = dld.DllName._decode(st_value)
        self.assertIn('biped.dlc', repr(dll_name))

    def test_decode_one_dll_description(self):
        ba_hex = (
            '39 20 '
            '3C 00 00 00 '
            '    42 00 69 00 70 00 65 00 64 00 20 00 43 00 6F 00 6E 00 74 00 72 00 6F 00 6C 00 6C 00 65 00 72 00 20 00 28 00 41 00 75 00 74 00 6F 00 64 00 65 00 73 00 6B 00 29 00'
        )
        st_value = utils.one_storage_from_ba_hex(ba_hex, self.valid_max_fname)
        dll_description = dld.DllDescription._decode(st_value)
        self.assertIn('Biped Controller (Autodesk)', repr(dll_description))

    def test_decode_one_dll_entry(self):
        ba_hex = (
            '38 20 '
            '5A 00 00 80 '
            '   39 20 '
            '   3C 00 00 00 '
            '       42 00 69 00 70 00 65 00 64 00 20 00 43 00 6F 00 6E 00 74 00 72 00 6F 00 6C 00 6C 00 65 00 72 00 20 00 28 00 41 00 75 00 74 00 6F 00 64 00 65 00 73 00 6B 00 29 00'
            '   37 20 '
            '   18 00 00 00 '
            '       62 00 69 00 70 00 65 00 64 00 2E 00 64 00 6C 00 63 00'
        )
        st_container = utils.one_storage_from_ba_hex(ba_hex, self.valid_max_fname)
        dll_entry = dld.DllDecoder._decode_one(st_container)

        dll_entry_ref = dld.DllEntry._decode(st_container)
        dll_entry_ref.childs = [
                dld.DllDescription._decode(st_container.childs[0]),
                dld.DllName._decode(st_container.childs[1]),
        ]

        self.assertEqual(dll_entry, dll_entry_ref)

    def test_decode_many_dll_entries(self):
        ba_hex = (
            '38 20 '
            '5A 00 00 80 '
            '   39 20 '
            '   3C 00 00 00 '
            '       42 00 69 00 70 00 65 00 64 00 20 00 43 00 6F 00 6E 00 74 00 72 00 6F 00 6C 00 6C 00 65 00 72 00 20 00 28 00 41 00 75 00 74 00 6F 00 64 00 65 00 73 00 6B 00 29 00'
            '   37 20 '
            '   18 00 00 00 '
            '       62 00 69 00 70 00 65 00 64 00 2E 00 64 00 6C 00 63 00'
            '38 20 '
            '86 00 00 80 '
            '   39 20 '
            '   54 00 00 00 '
            '       56 00 69 00 65 00 77 00 70 00 6F 00 72 00 74 00 20 00 4D 00 61 00 6E 00 61 00 67 00 65 00 72 00 20 00 66 00 6F 00 72 00 20 00 44 00 69 00 72 00 65 00 63 00 74 00 58 00 20 00 28 00 41 00 75 00 74 00 6F 00 64 00 65 00 73 00 6B 00 29 00 '
            '   37 20 '
            '   2C 00 00 00 '
            '       76 00 69 00 65 00 77 00 70 00 6F 00 72 00 74 00 6D 00 61 00 6E 00 61 00 67 00 65 00 72 00 2E 00 67 00 75 00 70 00'
        )
        st_containers = utils.all_storages_from_ba_hex(ba_hex, self.valid_max_fname)
        dll_entries = dld.DllDecoder._decode_many(st_containers)

        dll_entry_ref_1 = dld.DllEntry._decode(st_containers[0])
        dll_entry_ref_1.childs = [
                dld.DllDescription._decode(st_containers[0].childs[0]),
                dld.DllName._decode(st_containers[0].childs[1]),
        ]

        dll_entry_ref_2 = dld.DllEntry._decode(st_containers[1])
        dll_entry_ref_2.childs = [
                dld.DllDescription._decode(st_containers[1].childs[0]),
                dld.DllName._decode(st_containers[1].childs[1]),
        ]
        dll_entries_ref = [
            dll_entry_ref_1,
            dll_entry_ref_2,
        ]

        self.assertEqual(dll_entries, dll_entries_ref)
