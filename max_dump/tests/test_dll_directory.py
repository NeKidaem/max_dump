"""Unit tests for dll_directory.
"""
import unittest

import max_dump.storage_parser as sp
import max_dump.dll_directory as dld


class DllDecoderTests(unittest.TestCase):
    def test_decode_one_header(self):
        ba = ('C0 21 '
              '0A 00 00 00 '
              '69 03 50 46')
