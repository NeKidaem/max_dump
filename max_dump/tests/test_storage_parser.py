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
        with self.assertRaises(FileNotFoundError):
            sp.StorageParser("invalid_max_fname", "invalid_stream_name")

        valid_max_fname = BASE_DIR / "./data/01-teapot_no_cams_vray.max"
        with self.assertRaises(ValueError):
            sp.StorageParser(valid_max_fname, "invalid_stream_name")

