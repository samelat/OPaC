
import string
import random

from opac.opac_tree import PathNode


''' ################################
        PUBLIC - OPAC CLASS
    ################################
'''
class OPaC:
    def __init__(self):
        self.paths = []
        self.trees = {}

    def __iter__(self):
        return self

    def __next__(self):
        try:
            request = self.paths.pop()
            return request
        except IndexError:
            raise StopIteration

    def size(self):
        return len(self.paths)

    def add_path(self, complete_path):
        
        clean_path = complete_path.strip('/')

        if clean_path:
            splitted_path = clean_path.split('/')

            depth = len(splitted_path)

            if depth not in self.trees:
                self.trees[depth] = PathNode('')

            if self.trees[depth].add_path(splitted_path):
                self.paths.append(complete_path)
                return True

        return False
