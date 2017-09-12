"""Not yet a unittest.
"""
import os
import json
import unittest
import pathlib

import attr

import max_dump
from max_dump.storage_parser import extract_vpq


BASE_DIR = pathlib.Path(__file__).parent


class SimpleTest(unittest.TestCase):
    def test_extract(self):
        max_fname = str(BASE_DIR / 'data/01-teapot_no_cams_vray.max')
        storage = extract_vpq(max_fname)
        serialized = json.dumps(storage, sort_keys=True, indent=4)

        res_json = str(BASE_DIR / './data/01-teapot_no_cams_vray_storage_vpq.json')
        with open(res_json) as fin:
            serialized_old = fin.read().strip()
        self.assertEqual(serialized, serialized_old)