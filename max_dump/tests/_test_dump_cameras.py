"""Not yet a unittest.
"""
import os
import json
import unittest
import pathlib

import max_dump
from max_dump.dump_cameras import dump_cameras

BASE_DIR = pathlib.Path(__file__).parent


class SimpleTest(unittest.TestCase):
    def test_dump_cameras(self):
        max_fname = str(BASE_DIR / 'data/07-standard-17_physical_cameras.max')
        res_json = str(BASE_DIR / 'data/07-standard-17_physical_cameras.json')
        cams = dump_cameras(max_fname)
        with open(res_json) as fin:
            cams_old = json.load(fin)
        self.assertEqual(cams, cams_old)
