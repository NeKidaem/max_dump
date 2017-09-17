import io
import unittest


from max_dump import utils


class UtilsTest(unittest.TestCase):
    def test_read_short(self):
        size = utils.SHORT_S
        n = 42
        n_bytes = n.to_bytes(size, 'little', signed=True)
        r = utils.read_short(io.BytesIO(n_bytes))
        self.assertEqual(n, r)

    def test_read_short_negative(self):
        size = utils.SHORT_S
        n = -42
        n_bytes = n.to_bytes(size, 'little', signed=True)
        r = utils.read_short(io.BytesIO(n_bytes))
        self.assertEqual(n, r)

    def test_read_int(self):
        size = utils.INT_S
        n = 42
        n_bytes = n.to_bytes(size, 'little', signed=True)
        r = utils.read_short(io.BytesIO(n_bytes))
        self.assertEqual(n, r)

    def test_read_long_long(self):
        size = utils.LONG_LONG_S
        n = 42
        n_bytes = n.to_bytes(size, 'little', signed=True)
        r = utils.read_short(io.BytesIO(n_bytes))
        self.assertEqual(n, r)

    def test_unset_sign_bit_short(self):
        size = utils.SHORT_S
        a = -42
        b = utils.unset_sign_bit(a, size)
        self.assertEqual(b, 32726)
        a_hex = a.to_bytes(size, 'big', signed=True).hex()
        b_hex = b.to_bytes(size, 'big', signed=True).hex()
        self.assertEqual(a_hex, 'ffd6')
        self.assertEqual(b_hex, '7fd6')

    def test_unset_sign_bit_int(self):
        size = utils.INT_S
        a = -42
        b = utils.unset_sign_bit(a, size)
        self.assertEqual(b, 2147483606)
        a_hex = a.to_bytes(size, 'big', signed=True).hex()
        b_hex = b.to_bytes(size, 'big', signed=True).hex()
        self.assertEqual(a_hex, 'ffffffd6')
        self.assertEqual(b_hex, '7fffffd6')

    def test_unset_sign_bit_long(self):
        size = utils.LONG_LONG_S
        a = -42
        b = utils.unset_sign_bit(a, size)
        self.assertEqual(b, 9223372036854775766)
        a_hex = a.to_bytes(size, 'big', signed=True).hex()
        b_hex = b.to_bytes(size, 'big', signed=True).hex()
        self.assertEqual(a_hex, 'ffffffffffffffd6')
        self.assertEqual(b_hex, '7fffffffffffffd6')

    def test_index_by(self):
        l = [{"id": 1, "age": 30}, {"id": 2, "age": 31}, ]
        k = utils.index_by(l, "id")
        res = {1: {'age': 30, 'id': 1}, 2: {'age': 31, 'id': 2}}
        self.assertEqual(k , res)

    def test_index_by_nested(self):
        l = [{"id": 1, "age": 30, "person":{"name": "Mike"}},
             {"id": 2, "age": 31, "person":{"name": "Bob"}}, ]
        k = utils.index_by(l, "person__name")
        res = {'Bob': {'age': 31, 'id': 2, 'person': {'name': 'Bob'}},
               'Mike': {'age': 30, 'id': 1, 'person': {'name': 'Mike'}}}
        self.assertEqual(k , res)

    def test_index_by_overwrite_key(self):
        l = [{"id": 1, "age": 30},
             {"id": 2, "age": 31},
             {"id": 1, "age": 32}, ]
        k = utils.index_by(l, "id")
        res = {1: {'age': 32, 'id': 1}, 2: {'age': 31, 'id': 2}}
        self.assertEqual(k , res)

    def test_group_by(self):
        l = [{"id": 1, "age": 30},
             {"id": 2, "age": 31},
             {"id": 1, "age": 32}, ]
        k = utils.group_by(l, "id")
        res = {1: [{"id": 1, "age": 30}, {"id": 1, "age": 32}],
               2: [{'age': 31, 'id': 2}, ]}
        self.assertEqual(k , res)

    def test_group_by_nested(self):
        l = [
                {"id": 1, "age": 30, "person":{"name": "Mike"}},
                {"id": 2, "age": 31, "person":{"name": "Bob"}},
                {"id": 3, "age": 32, "person":{"name": "Mike"}},
        ]
        k = utils.group_by(l, "person__name")
        res = {
                'Mike': [
                    {"id": 1, "age": 30, "person":{"name": "Mike"}},
                    {"id": 3, "age": 32, "person":{"name": "Mike"}},
                ],
                'Bob': [
                    {"id": 2, "age": 31, "person":{"name": "Bob"}},
                ],
        }
        self.assertEqual(k , res)

