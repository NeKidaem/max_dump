"""Not yet a unittest.
"""
import os
import json
import unittest
import pathlib

import attr

import max_dump
from max_dump.storage_parser import extract_vpq, EnumEncoder


BASE_DIR = pathlib.Path(__file__).parent


class SimpleTest(unittest.TestCase):
    def test_extract(self):
        max_fname = str(BASE_DIR / 'data/01-teapot_no_cams_vray.max')
        c = extract_vpq(max_fname)
        d = attr.asdict(c)
        serialized = json.dumps(d, cls=EnumEncoder, sort_keys=True, indent=4)

        res_json = str(BASE_DIR / './data/01-teapot_no_cams_vray_storage_sorted.json')
        with open(res_json) as fin:
            serialized_old = fin.read().strip()
        self.assertEqual(serialized, serialized_old)

