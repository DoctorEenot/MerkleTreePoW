import hashlib
from typing import List, Tuple

from merkletree import MerkleTree
import time
import random


def HASH_FUNCTION(input): return hashlib.sha256(input).digest()


DIFFICULTY = 10000
''' amount of leaves, difficulty: (DIFFICULTY*2)-1 - hashes required in total'''
PREV_BLOCK_HASH = b'qwertyuiopasdfghjklzxcvbnmasdfew'
TIMESTAMP = int(time.time())
''' timestamp of the last block '''
MASK = 0b01111111


def num_to_bytes(number: int) -> bytes:
    '''
    Basically it just uses the lowest amount of bytes to represent a number in a big endian notation
    '''
    to_return = b''
    if number != 0:
        i_clone = number
        while i_clone > 0:
            to_return = (i_clone & 0xff).to_bytes(1, 'big') + to_return
            i_clone >>= 8
    else:
        to_return = b'\x00'

    return to_return


def generate_initial_data(prev_hash: bytes,
                          difficulty: int,
                          nonce: bytes) -> List[bytes]:
    '''
    Generates initial data for a mining process

    The data is generated as a hash chain

    Hash(prev_hash+nonce)

        Parameters:
            prev_hash: bytes - hash of the previous block
            difficulty: int - difficulty
            nonce: bytes - a nonce to add for each iteration

        Returns:
            A list with hashes
    '''
    to_return = [prev_hash]
    for _ in range(difficulty-1):

        to_hash = prev_hash + nonce

        hash = HASH_FUNCTION(to_hash)
        to_return.append(hash)

        prev_hash = hash

    return to_return


def mine(prev_hash: bytes, difficulty: int, target: int) -> Tuple[List[bytes], bytes]:
    '''
    Proof of concept for a mining algorithm

    The nonce can be a string of bytes of an arbitrary length.

        Parameters:
            prev_hash: bytes - hash of the previous block
            difficulty: int - difficulty
            target: int - the target we are looking for

        Returns:
            A tuple with created proof and a nonce, in this exact order
    '''
    nonce = 0

    while True:
        # generate leaves with a nonce
        initial_data = generate_initial_data(
            prev_hash, difficulty, nonce.to_bytes(8, 'big'))

        # create merkle tree from leaves
        tree = MerkleTree(HASH_FUNCTION, initial_data)

        # build the tree
        tree.build_tree()

        # apply a mask to the calculated root to make the hash into a number in the range [0, MASK]
        num = int.from_bytes(tree.root, 'big') % (MASK+1)

        # if the found number is equal to the target - return found data
        if num == target:
            return (tree.get_proof(0), nonce.to_bytes(8, 'big'))

        nonce += 1


def verification(prev_hash: bytes, difficulty: int, nonce: bytes, proof: List[bytes], root: bytes, target: int):
    '''
    calculated PoW verification
    '''
    initial_data = generate_initial_data(
        prev_hash, difficulty, nonce)
    proof.insert(0, initial_data[1])
    is_valid = MerkleTree.verify(
        PREV_BLOCK_HASH, proof, root, HASH_FUNCTION)
    print("proof is valid:", is_valid)

    print("Target reached:", int.from_bytes(root, 'big') % (MASK+1) == target)


def main():
    global DIFFICULTY, PREV_BLOCK_HASH, TIMESTAMP

    target = random.randint(0, MASK)
    print("Target:", target)

    start_mining = time.time()
    mined_proof, nonce = mine(
        PREV_BLOCK_HASH, DIFFICULTY, target)
    delta_mining = time.time() - start_mining
    print("Time taken by mining:", delta_mining)

    proof = mined_proof[1:-1]  # similar to what the node will receive

    start_verification = time.time()
    verification(PREV_BLOCK_HASH, DIFFICULTY, nonce,
                 proof, mined_proof[-1], target)
    delta_verification = time.time() - start_verification
    print("Time taken by verification:", delta_verification)

    print(f"Verification was {delta_mining/delta_verification} times faster")


if __name__ == "__main__":
    main()
