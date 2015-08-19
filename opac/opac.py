
import string
import random

from opac_tree import PathNode


''' ################################
        PUBLIC - OPAC CLASS
    ################################
'''
class OPaC:
    def __init__(self):
        self.paths = []
        self.trees = {}
        self.count = 0

    def __iter__(self):
        return self

    def next(self):
        if not self.paths:
            raise StopIteration
        else:
            return self.paths.pop()


    def size(self):
        return sum([tree.weight for tree in self.trees])


    def add_path(self, path):

        path = path.strip('/')
        if path:
            spath = path.split('/')

            depth = len(spath)

            if depth not in self.trees:
                self.trees[depth] = PathNode('')

            if self.trees[depth].add_path(spath):
                self.count += 1
                return True

        return False
