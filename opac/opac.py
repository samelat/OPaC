
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
        self.refresh_root = ''

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

    def add_tree_path(self, complete_path):
        clean_path = complete_path.strip('/')
        if clean_path:
            splitted_path = clean_path.split('/')

            depth = len(splitted_path)
            if depth not in self.trees:
                self.trees[depth] = PathNode(name='', callback=self.refresh_callback)
            return self.trees[depth].add_path(splitted_path):

        return False

    def add_path(self, complete_path):
        if self.add_tree_path(complete_path):
            self.paths.append(complete_path)

            if self.refresh_root:
                self.refresh()
            return True

        return False

    ''' Refresh routines
    '''
    def refresh_callback(self, opac_node):
        self.refresh_root = opac_node.get_root()
        print('[!] REFRESH!: {0}'.format(self.refresh_root))

    def refresh(self):
        paths = []
        for path in self.paths:
            if re.match('^' + self.refresh_root, path) and self
