from collections import defaultdict
from struct import unpack, calcsize

INT_S = calcsize('i')
SHORT_S = calcsize('h')


def read_int(bio):
    return unpack('i', bio.read(INT_S))[0]


def _new_key(entry, key):
    new_key = entry
    for sub_key in key.split('__'):
        new_key = new_key[sub_key]
    return new_key


def index_by(iterable, key):
    """Return a dictionary from the given iterable.

    `key' may be nested like that: 'header__idn'
    >>> l = [{"id": 1, "age": 35}, {"id": 2, "age": 32}, ]
    >>> index_by(l, "id")
    {1: {'age': 35, 'id': 1}, 2: {'age': 32, 'id': 2}}

    >>> l = [{"id": 1, "age": 35, "person":{"name": "Mike"}}, {"id": 2, "age": 32, "person":{"name": "Bob"}}, ]
    >>> index_by(l, "person__name")
    {'Bob': {'age': 32, 'id': 2, 'person': {'name': 'Bob'}},
     'Mike': {'age': 35, 'id': 1, 'person': {'name': 'Mike'}}}
    """
    indexed = {}
    for entry in iterable:
        new_key = _new_key(entry, key)
        indexed[new_key] = entry
    return indexed


def group_by(iterable, key):
    grouped = defaultdict(list)
    for entry in iterable:
        new_key = _new_key(entry, key)
        grouped[new_key].append(entry)
    return grouped


