#!/usr/bin/python

from types import *
from base64 import b32encode
from mhash import MHASH, MHASH_TIGER

def tiger(chunk):
    '''Hashes the string parameter'''
    return MHASH(MHASH_TIGER, chunk).digest()


class node(object):
    '''Represents a node in the tiger tree hash'''
    def __init__(self, leaves):
        self.leaves = None

        if len(leaves) > 1:
            self.value = tiger(reduce(lambda a,b:a+b, map(str, leaves)))
            self.leaves = leaves
        else:
            if type(leaves[0]) == node:
                self.value = leaves[0]
            else:
                self.value = tiger(leaves[0])

    def encode(self):
        '''Returns the base32 encoding of the hash at this node'''
        if type(self.value) == node:
            return self.value.encode()
        return b32encode(self.value)

    def __str__(self):
        if type(self.value) == node:
            return str(self.value)
        return self.value

    def __repr__(self):
        return "<TTH node: '%s', %s>" % (self.encode(), repr(self.leaves))

class TigerTreeHash(object):
    '''Represents the tiger tree hash object'''
    def __init__(self, f, segment=1024):
        self.segment = segment
        self.buf = None
        self.fp = None
        if type(f) == StringType:
            self.buf = f
        elif type(f) == file:
            self.fp = f
        else:
            raise TypeError("f must be a string or file object")

        self.root = self.doFullTree()

    def depth(self):
        d = 0
        t = self.root
        while t:
            d += 1
            if type(t) == node:
                t = t.leaves
            else:
                t = t[0].leaves
        return d

    def doFullTree(self):
        '''Runs the full hash and returns the tree as a nested list of nodes'''
        if self.buf:
            return self.doFullTree_buf()
        if self.fp:
            return self.doFullTree_fp()

    def doFullTree_buf(self):
        pass

    def doFullTree_fp(self):
        leaves = []
        while True:
            chunk = self.fp.read(self.segment)
            if not chunk:
                break
            
            leaves.append(node([chunk]))

        while True:
            tree = [node(leaves[i:i+2]) for i in range(0, len(leaves), 2)]
            if (len(tree) > 1):
                leaves = tree
            else:
                return tree[0]


if __name__ == '__main__':
    import sys
    import pprint
    t = TigerTreeHash(open(sys.argv[1]))
    #print repr(t.root)
    print 'depth', t.depth()
