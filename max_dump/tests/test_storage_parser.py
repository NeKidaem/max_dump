"""Not yet a unittest.
"""
import io
import unittest
import pathlib

import max_dump.storage_parser as sp


BASE_DIR = pathlib.Path(__file__).parent


class StorageParserTest(unittest.TestCase):
    def setUp(self):
        self.valid_max_fname = BASE_DIR / "./data/01-teapot_no_cams_vray.max"
        self.valid_stream_name = 'ClassData'

    def test_init(self):
        with self.assertRaises(ValueError):
            sp.StorageParser("invalid_max_fname")

    def test_read_stream(self):
        parser = sp.StorageParser(self.valid_max_fname)

        with self.assertRaises(ValueError):
            parser._read_stream("invalid_stream_name")

        stream = parser._read_stream(self.valid_stream_name)
        self.assertIsInstance(stream, io.BytesIO)

    def test_read_header_value(self):
        # binary header, value
        ba_hex = (
                '50 00 '  # idn (identifier)
                '0a 00 00 00'  # length without sign bit (positive)
        )
        ba = bytes.fromhex(ba_hex)
        parser = sp.StorageParser(self.valid_max_fname)
        parser._stream = io.BytesIO(ba)
        header = parser._read_header()
        res_header = sp.StorageHeader(idn=80, length=4,
                                      storage_type=sp.StorageType.VALUE,
                                      extended=False)
        self.assertEqual(header, res_header)

    def test_read_header_container(self):
        # binary header, container
        ba_hex = (
                '50 00 '  # idn (identifier)
                '0a 00 00 80'  # length with sign bit (negative)
        )
        ba = bytes.fromhex(ba_hex)
        parser = sp.StorageParser(self.valid_max_fname)
        parser._stream = io.BytesIO(ba)
        header = parser._read_header()
        res_header = sp.StorageHeader(idn=80, length=4,
                                      storage_type=sp.StorageType.CONTAINER,
                                      extended=False)
        self.assertEqual(header, res_header)

    def test_read_header_extended_value(self):
        # binary extended header, value
        ba_hex = (
                '50 00 '  # idn (identifier)
                '00 00 00 00 '  # zero-length, indicates extended header
                '12 00 00 00 00 00 00 00'  # 8-byte length
        )
        ba = bytes.fromhex(ba_hex)
        parser = sp.StorageParser(self.valid_max_fname)
        parser._stream = io.BytesIO(ba)
        header = parser._read_header()
        res_header = sp.StorageHeader(idn=80, length=4,
                                      storage_type=sp.StorageType.VALUE,
                                      extended=True)
        self.assertEqual(header, res_header)

    def test_read_header_extended_container(self):
        # binary extended header, container
        ba_hex = (
                '50 00 '  # idn (identifier)
                '00 00 00 00 '  # zero-length, indicates extended header
                '12 00 00 00 00 00 00 80'  # 8-byte length
        )
        ba = bytes.fromhex(ba_hex)
        parser = sp.StorageParser(self.valid_max_fname)
        parser._stream = io.BytesIO(ba)
        header = parser._read_header()
        res_header = sp.StorageHeader(idn=80, length=4,
                                      storage_type=sp.StorageType.CONTAINER,
                                      extended=True)
        self.assertEqual(header, res_header)
