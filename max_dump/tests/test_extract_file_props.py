"""Not yet a unittest.
"""
import os
import json
import unittest
import pathlib

import max_dump
from max_dump.file_props_parser import extract_file_props


BASE_DIR = pathlib.Path(__file__).parent


class SimpleTest(unittest.TestCase):
    def test_extract(self):
        max_fname = str(BASE_DIR / 'data/01-teapot_no_cams_vray.max')
        res_json = str(BASE_DIR / 'data/01-teapot_no_cams_vray_props.json')
        p1 = extract_file_props(max_fname)
        with open(res_json) as fin:
            p2 = json.load(fin)
        self.assertEqual(p1, p2)
