
import string
import random

from path_tree import PathNode


''' ################################
        PUBLIC - OPAC CLASS
    ################################
'''
class OPaC:
    def __init__(self):
        self.limit_per_filter_entry = 4
        self.paths = set([])
        self.saw_paths = set([])
        self.filters = {}
        self.trees = {}


    def __iter__(self):
        return self


    def next(self):
        if not self.paths:
            raise StopIteration
        else:
            path = self.paths.pop()
            self.saw_paths.add(path)
            self.takenA += 1
            return path


    def size(self):
        return self.tree.weight


    def add_path(self, path):
        if (path in self.paths) or (path in self.saw_paths):
            return False

        spath = path.strip('/').split('/')
        if spath:
            # "remaining" is the number of matches we allow to exist per regex
            # before deny all of them.

            depth = len(spath)

            if depth not in self.trees:
                self.trees[depth] = PathNode('', weight=0)

            self.trees[depth].add_path(spath)

            '''
            for _sfilter, (_cfilter, remaining) in self.filters.iteritems():
                if _cfilter.match(path):
                    if remaining:
                        self.filters[_sfilter] = (_cfilter, remaining - 1)
                        self.paths.add(path)
                        return True
                    return False
            self.tree.add_path(spath)
            self.paths.add(path)
            return True
            '''

        return False


    '''
        Obtenemos todos los nodos que tienen claras caracteristicas que los
        hacen suprimibles.
    ''' 
    def clean(self):
        if self.tree.is_empty():
            return False

        weight_e, weight_devn = self.tree.distribution()
        
        heavy_nodes = self.tree.heaviers(weight_e + weight_devn)

        scrap = []
        for node in heavy_nodes:
            _scrap = node.get_scrap(weight_e + weight_devn)
            scrap.extend(_scrap)

        survivor_paths = self.paths
        for _scrap in scrap:
            regexes = _scrap.get_regexes()

            _sfilter =  '^/' + '/'.join(regexes) + '/?$'

            _cfilter = re.compile(_sfilter)

            #print _sfilter

            _scrap.clean()

            self.filters[_sfilter] = (_cfilter, self.limit_per_filter_entry)
            _tmp = []
            for path in survivor_paths:
                if _cfilter.match(path):
                    self.saw_paths.add(path)
                else:
                    _tmp.append(path)
            survivor_paths = _tmp

        self.paths = set(survivor_paths)

