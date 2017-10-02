"""Unit tests for class_directory_3.
"""
import unittest
import pathlib

import max_dump.storage_parser as sp
import max_dump.dll_directory as dld
import max_dump.class_directory_3 as cd
from . import utils


BASE_DIR = pathlib.Path(__file__).parent


class ClassDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.valid_max_fname = BASE_DIR / "./data/01-teapot_no_cams_vray.max"

    def test_decode_class_header(self):
        ba_hex = (
            '60 20 '
            '16 00 00 00 '
            '   FF FF FF FF 8F F5 01 00 9F A2 03 00 60 11 00 00'
        )
        st_value = utils.one_storage_from_ba_hex(ba_hex, self.valid_max_fname)
        decoded_header = cd.ClassDecoder()._decode_one(st_value)
        header = cd.ClassHeader(
                dll_index=-1,
                class_id=(0x1f58f, 0x3a29f),
                super_class_id=0x1160,
        )
        self.assertEqual(header, decoded_header)

    def test_decode_class_name(self):
        ba_hex = (
            '42 20 '
            '30 00 00 00 '
            '   41 00 6E 00 63 00 68 00 6F 00 72 00 43 00 75 00 73 00 74 00 6F 00 6D 00 41 00 74 00 74 00 72 00 69 00 62 00 75 00 74 00 65 00'
        )
        st_value = utils.one_storage_from_ba_hex(ba_hex, self.valid_max_fname)
        decoded_name = cd.ClassDecoder()._decode_one(st_value)
        name = cd.ClassName(
                decoded='AnchorCustomAttribute',
        )
        self.assertEqual(name, decoded_name)

    def test_decode_class_entry(self):
        ba_hex = (
            '40 20 '
            '4C 00 00 80 '
            '   60 20 '
            '   16 00 00 00 '
            '       FF FF FF FF 8F F5 01 00 9F A2 03 00 60 11 00 00 '
            '   42 20 '
            '   30 00 00 00 '
            '       41 00 6E 00 63 00 68 00 6F 00 72 00 43 00 75 00 73 00 74 00 6F 00 6D 00 41 00 74 00 74 00 72 00 69 00 62 00 75 00 74 00 65 00'
        )
        st_cont = utils.one_storage_from_ba_hex(ba_hex, self.valid_max_fname)
        decoded_entry = cd.ClassDecoder()._decode_one(st_cont)

        entry = cd.ClassEntry(
            header=cd.ClassHeader(
                dll_index=-1,
                class_id=(0x1f58f, 0x3a29f),
                super_class_id=0x1160,
            ),
            name=cd.ClassName(
                decoded='AnchorCustomAttribute',
            ),
        )

        self.assertEqual(decoded_entry, entry)

    #  def test_link_builtin_class_entry(self):
        #  raise NotImplementedError()
