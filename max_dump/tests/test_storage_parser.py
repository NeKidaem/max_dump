"""Unit tests for storage_parser.
"""
import io
import unittest
import olefile
import pathlib

import max_dump.storage_parser as sp


BASE_DIR = pathlib.Path(__file__).parent


class InitTests(unittest.TestCase):
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


class ReadHeaderTests(unittest.TestCase):
    def test_read_header_value(self):
        # binary header, value
        ba_hex = (
            '50 00 '  # idn (identifier)
            '0a 00 00 00'  # length without sign bit (positive)
        )
        ba = bytes.fromhex(ba_hex)
        ba_stream = io.BytesIO(ba)
        header = sp.StorageHeader.from_bytes(ba_stream)
        ref_header = sp.StorageHeader(idn=80, length=4,
                                      storage_type=sp.StorageType.VALUE,
                                      extended=False)
        self.assertEqual(header, ref_header)

    def test_read_header_container(self):
        # binary header, container
        ba_hex = (
            '50 00 '  # idn (identifier)
            '0a 00 00 80'  # length with sign bit (negative)
        )
        ba = bytes.fromhex(ba_hex)
        ba_stream = io.BytesIO(ba)
        header = sp.StorageHeader.from_bytes(ba_stream)
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
        ba_stream = io.BytesIO(ba)
        header = sp.StorageHeader.from_bytes(ba_stream)
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
        ba_stream = io.BytesIO(ba)
        header = sp.StorageHeader.from_bytes(ba_stream)
        res_header = sp.StorageHeader(idn=80, length=4,
                                      storage_type=sp.StorageType.CONTAINER,
                                      extended=True)
        self.assertEqual(header, res_header)


class ReadNodesTests(unittest.TestCase):
    def setUp(self):
        self.valid_max_fname = BASE_DIR / "./data/01-teapot_no_cams_vray.max"

    def test_read_one_simple_node(self):
        ba_hex = (
            '50 00 '  # idn (identifier)
            '0a 00 00 00 '  # length without sign bit (positive)
            '   01 00 00 00 '  # some value
        )
        ba = bytes.fromhex(ba_hex)
        parser = sp.StorageParser(self.valid_max_fname)
        parser._stream = io.BytesIO(ba)
        header = sp.StorageHeader.from_bytes(parser._stream)
        node = parser._read_one_storage(header)

        res_header = sp.StorageHeader(idn=80, length=4,
                                      storage_type=sp.StorageType.VALUE,
                                      extended=False)
        res_value = bytes.fromhex('01 00 00 00')
        res_storage = sp.StorageValue(header=res_header, value=res_value,
                                      nest=0)

        self.assertEqual(node, res_storage)

    def test_read_few_simple_nodes(self):
        ba_hex = (
            '50 00 '  # idn (identifier)
            '0A 00 00 00 '
            '   01 00 00 00 '
            '60 00 '
            '2A 00 00 80 '  # length with sign bit, it is a container
            '   10 00 '
            '   1E 00 00 00 '
            '       07 00 00 00 '
            '       01 00 00 00 '
            '       00 00 00 00 '
            '       00 00 00 00 '
            '       20 12 00 00 '
            '       00 00 00 00 '
            '   20 00 '
            '   06 00 00 00 '
        )

        ba = bytes.fromhex(ba_hex)
        parser = sp.StorageParser(self.valid_max_fname)
        parser._stream = io.BytesIO(ba)
        nodes = parser.read_storages(len(ba))

        first_header = sp.StorageHeader(idn=80, length=4,
                                        storage_type=sp.StorageType.VALUE,
                                        extended=False)
        first_value = bytes.fromhex('01 00 00 00')
        storage_value = sp.StorageValue(header=first_header,
                                        value=first_value, nest=1)

        container_header = sp.StorageHeader(
            idn=96, length=36, storage_type=sp.StorageType.CONTAINER,
            extended=False
        )

        first_child = sp.StorageValue(
            header=sp.StorageHeader(
                idn=16, length=24, storage_type=sp.StorageType.VALUE,
                extended=False
            ),
            value=bytes.fromhex(
                '07 00 00 00 '
                '01 00 00 00 '
                '00 00 00 00 '
                '00 00 00 00 '
                '20 12 00 00 '
                '00 00 00 00 '
            ),
            nest=2
        )
        second_child = sp.StorageValue(
            header=sp.StorageHeader(
                idn=32, length=0, storage_type=sp.StorageType.VALUE,
                extended=False
            ),
            value=b'',
            nest=2
        )

        storage_container = sp.StorageContainer(header=container_header,
                                                childs=[first_child,
                                                        second_child], nest=1)

        self.assertEqual(nodes, [storage_value, storage_container])


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.valid_max_fname = BASE_DIR / "./data/2014_many_cams.max"

    def test_parse_stream(self):
        parser = sp.StorageParser(self.valid_max_fname)
        nodes = parser.parse_stream('VideoPostQueue')

        res_nodes = [
            sp.StorageValue(
                header=sp.StorageHeader(
                    idn=80, length=4, storage_type=sp.StorageType.VALUE,
                    extended=False
                ),
                value=b'\x00\x00\x00\x00',
                nest=1
            ),
            sp.StorageValue(
                header=sp.StorageHeader(
                    idn=96, length=0, storage_type=sp.StorageType.VALUE,
                    extended=False),
                value=b'',
                nest=1
            )
        ]
        self.assertEqual(nodes, res_nodes)

    def test_read_stream_not_in_mem(self):
        parser = sp.StorageParser(self.valid_max_fname)
        try:
            stream = parser._read_stream('VideoPostQueue', in_mem=False)
            self.assertIsInstance(parser._ole, olefile.OleFileIO)
        finally:
            if parser._ole:
                parser._ole.close()

    def test_parse_stream_not_in_mem(self):
        parser = sp.StorageParser(self.valid_max_fname)
        nodes = parser.parse_stream('VideoPostQueue', in_mem=False)

        res_nodes = [
            sp.StorageValue(
                header=sp.StorageHeader(
                    idn=80, length=4, storage_type=sp.StorageType.VALUE,
                    extended=False
                ),
                value=b'\x00\x00\x00\x00',
                nest=1
            ),
            sp.StorageValue(
                header=sp.StorageHeader(
                    idn=96, length=0, storage_type=sp.StorageType.VALUE,
                    extended=False),
                value=b'',
                nest=1
            )
        ]
        self.assertEqual(nodes, res_nodes)
