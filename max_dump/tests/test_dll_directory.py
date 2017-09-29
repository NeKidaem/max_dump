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

    def test_decode_one_header(self):
        ba_hex = (
            'C0 21 '
            '0A 00 00 00 '
            '   69 03 50 46'
        )
        storage = utils.one_storage_from_ba_hex(ba_hex, self.valid_max_fname)
