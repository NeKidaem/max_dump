import abc


class AbstractDecoder(abc.ABC):
    idn2class_map = {}
    CONTAINERS = {}
    NODES = {}

    def decode(self, nodes):
        return self._decode_many(nodes)

    def _decode_many(self, nodes):
        return [self._decode_one(node) for node in nodes]

    def _decode_one(self, node):
        idn = node.idn

        if idn not in self.idn2class_map:
            self._raise_unknown_id_exc(idn)

        klass = self.idn2class_map[idn]
        decoded_node = klass._decode(node)

        if idn in self.CONTAINERS:
            decoded_node.childs = self._decode_many(node.childs)

        return decoded_node

    @staticmethod
    @abc.abstractmethod
    def _raise_unknown_id_exc(self, idn):
        raise NotImplementedError()
