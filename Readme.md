# Merkle Tree based proof of work



# Why?

Why to bother with a new PoW scheme and why Bitcoin PoW sucks, you might wander.

If you don't, then you probably not very familiar with the classic PoW.

Let me explain, in the classic PoW algorithms, you have an input data(transactions, block info and other stuff) you add a nonce to it and after hashing you check if the amount of leading zeros you got satisfies the current difficulty/target.

If you didn't know the nonce size in Bitcoin is 4 bytes long. In the modern days miners also alter timestamp, transactions and everything, that can be altered in the block to get a different hash, the miner will try to alter. This is done purely out of despair, since 4 bytes nonce practically might not be enough to get a required hash. 

Also let's not forget about unpredictable nature of mining, with classical PoW there is too much outcomes for the hash, and to be real, it should be called Proof-of-Luck.

With this algorithm I aim to beat this problem, the algorithm I propose aims to allow miners to change only the nonce, while stil being able to solve the puzzle. But that's not the best part. The best part of this algorithm is actually being a Proof-of-Work, as the miner will have to <\<present\>> almost all the work it has done.

Feel interested? Continue reading! The deeper - the more interesting.

# Basics needed to undersand this paper

So, the requirements are pretty simple, you have to understand [Merkle tree](https://en.wikipedia.org/wiki/Merkle_tree) and [Hash Chain](https://en.wikipedia.org/wiki/Hash_chain). I suggest reading about them first, as I will not be explaining their inner workings.

# The Holy Algorithm

So, the algorithm. I will go through the way I see it's working in the pair Node/Network-miner.

1. The Network has to have some mechanism of generating veryfiable target. Lets say for now target = Sha256(last_block_hash+last_block_timestamp+MAGIC_NUMBER) % (MASK+1)
    
    That's a lot already, isn't it? So the data in the Sha256() might be anything you want, but it has to be uniform across the network. Every Node should get the same data.

    MASK - that's the key idea of this algorithm. So, the target, an unsigned integer, should be in this range [0, MASK+1], so in the line above we get the target to be in this range. As you might understand the value of Mask should also be uniform across the network.

2. After sending the target, difficulty and all the needed data to the miner, miner starts mining.
    
    The difficulty shows us how much leaves the merkle tree will have
    * So, first, we create some leaves for our merkle tree. To do so, we will be using Hash Chains, so the next hash will have previous one inside. To every hash we add a nonce, somehow. The way nonce is added and the way leaves are generated is not strictly defined and can be changed, but the main idea is to make it uniform, so that anyone in the network will do same steps and get absolutely the same data.
    * After we created leaves, we create and build out Merkle Tree. This process will take a while, as the amount of hashing operations per one tree will require 2^tree_depth - (DIFFICULTY + 1) hashing operations
    * After the tree is built, we take our calculated root, calclate a target Sha256(last_block_hash+last_block_timestamp+MAGIC_NUMBER) % (MASK+1) and compare it to the target of the network.
    * If the target was right - congrats you found the right nonce, now build a proof for the first leaf(any leaf, but again, it should be uniform across the network) and send the proof, nonce, root to the node. If the target wasn't right, change/increase nonce start from the beginning.

3. The node received the proof of work. now it will verify it.
    * Things to verify: 
        * Right amount of supplied nodes in the tree proof, it will be equal to the height - 2(-2 if we don't include root and the leaf to the proof)
        * Verify that the target is indeed right
        * And eventually after all the previous checks have passed - verify the tree proof.
    * If the verification was successful, congrats, the block has been mined.

### Considerations:
* The mask should not be too big, I would suggest not larger, than 255
* Ideally the merkle tree implementation should always have amount of leaves equal to some power of 2.


# The algorithm is yet to be auditted and proved, that it's in fact safe and doesn't have vulnerabilities.

