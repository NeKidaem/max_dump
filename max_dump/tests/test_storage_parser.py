"""Not yet a unittest.
"""
import os
import json
import unittest
import pathlib

import attr

import max_dump
import max_dump.storage_parser as sp


BASE_DIR = pathlib.Path(__file__).parent


class StorageParserTest(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            sp.StorageParser("invalid_max_fname")

        valid_max_fname = BASE_DIR / "./data/01-teapot_no_cams_vray.max"
        parser = sp.StorageParser(valid_max_fname)
        with self.assertRaises(ValueError):
            parser.read_stream("invalid_stream_name")

