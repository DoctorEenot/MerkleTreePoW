import hashlib
import binascii
from typing import overload, List, Tuple
from collections.abc import Callable


def find_closest_power_of_2(number: int) -> int:
    power = 0
    x = 1
    while x < number:
        power += 1
        x <<= 1
    return power


DEFAULT_PADDING_HASH = b'\xff'*32


class MerkleTree:
    def __init__(self,
                 hash_function: Callable[[bytes | str], bytes],
                 leaves: List[bytes | str],
                 padding_hash=DEFAULT_PADDING_HASH):

        self.hash_function = hash_function
        self.__leaves = leaves
        self.__depth = 0
        self.__padding_hash = padding_hash

        if len(self.__leaves) % 2 != 0:
            self.__depth = find_closest_power_of_2(len(self.__leaves)) + 1
            size = 2**(self.__depth-1)
            self.__depth = find_closest_power_of_2(size)
            for _ in range(size-len(self.__leaves)):
                self.__leaves.append(self.__padding_hash)
        else:
            self.__depth = find_closest_power_of_2(len(self.__leaves)) + 1

        self.__array_representation = []
        amount_of_nodes = (len(self.__leaves)*2) - 1

        for _ in range(amount_of_nodes - len(self.__leaves)):
            self.__array_representation.append(None)

        for leaf in self.__leaves:
            self.__array_representation.append(leaf)

    def __calculate_boundaries(depth: int) -> Tuple[int, int]:
        '''
        Calculates layer length and it's starting index
        '''
        layer_length = 2**(depth-1)
        return (layer_length, layer_length - 1)

    def calculate_parents(self, depth: int) -> List[bytes]:
        to_return = []
        layer_length, starting_index = MerkleTree.__calculate_boundaries(depth)

        slice = self.__array_representation[starting_index:starting_index+layer_length]

        left_leaf_iter = iter(slice[::1])
        right_leaf_iter = iter(slice[1::2])
        for left_leaf, right_leaf in zip(left_leaf_iter, right_leaf_iter):
            combined_input = []
            for left_byte, right_byte in zip(left_leaf, right_leaf):
                combined_input.append(left_byte & right_byte)

            to_return.append(self.hash_function(bytes(combined_input)))

        layer_length, starting_index = MerkleTree.__calculate_boundaries(
            depth-1)

        self.__array_representation[starting_index:starting_index +
                                    layer_length] = to_return

        return to_return

    def build_tree(self):
        for depth in range(self.__depth, 1, -1):
            self.calculate_parents(depth)

    def __get_proof_node(self, leaf_absolute_index: int, depth: int) -> int:
        # _, layer_index = MerkleTree.__calculate_boundaries(depth)

        # leaf_absolute_index = layer_index + leaf

        _, layer_index = MerkleTree.__calculate_boundaries(depth-1)

        parent_index = (leaf_absolute_index - 1) // 2

        parent_relative_index = parent_index - layer_index

        proof_node_index = 0
        if parent_relative_index % 2 == 0:
            # left node
            proof_node_index = parent_index + 1
        else:
            proof_node_index = parent_index - 1

        return proof_node_index

    def __get_sibling(self, leaf: int, depth: int) -> bytes:
        _, layer_index = MerkleTree.__calculate_boundaries(depth)

        relative_index = leaf - layer_index
        if relative_index % 2 == 0:
            return self.__array_representation[leaf + 1]
        else:
            return self.__array_representation[leaf - 1]

    def get_proof(self, leaf: int) -> List[bytes]:
        _, layer_index = MerkleTree.__calculate_boundaries(self.__depth)

        leaf = layer_index + leaf
        to_return = [self.__get_sibling(leaf, self.__depth)]

        for depth in range(self.__depth, 2, -1):
            leaf = self.__get_proof_node(leaf, depth)
            to_return.append(self.__array_representation[leaf])

        to_return.append(self.root)
        return to_return

    def verify(leaf: bytes, proof: List[bytes], root: bytes, hashing_function: Callable[[bytes | str], bytes]) -> bool:
        leaf = list(leaf)

        for pr in proof:
            new_leaf = []
            for leaf_byte, pr_byte in zip(leaf, pr):
                new_leaf.append(leaf_byte & pr_byte)

            leaf = list(hashing_function(bytes(new_leaf)))

        return bytes(leaf) == root

    @property
    def root(self) -> bytes:
        return self.__array_representation[0]


if __name__ == "__main__":
    leaves = [b'\x01'*32]*(2**20)
    tree = MerkleTree(lambda input: hashlib.sha256(input).digest(), leaves)

    tree.build_tree()

    proof = tree.get_proof(0)[:-1]

    verif = MerkleTree.verify(
        b'1'*32, proof, tree.root, lambda input: hashlib.sha256(input).digest())

    print()
