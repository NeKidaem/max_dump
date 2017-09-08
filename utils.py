from struct import unpack, calcsize

INT_S = calcsize('i')
SHORT_S = calcsize('h')


def read_int(bio):
    return unpack('i', bio.read(INT_S))[0]
