import re
import math
import string
import random

from opac_regex import OPaCRegex

''' ################################
        PRIVATE - SCRAP CLASS
    ################################
'''
class Scrap:
    def __init__(self, node, depth, weight):
        self.node   = node
        self.depth  = depth
        self.weight = weight

        self.regexes = []

    def __str__(self):
        return '[{0}] {1} | {2}'.format(self.node.name, self.depth, self.weight)

    '''
        Generates the regexes that better match with the scrap branch (one regex per level)
    '''
    def get_regexes(self):

        paths = self.node.paths_per_depth(self.depth)

        for index in range(self.depth - 1, -1, -1):
            column = [path[index] for path in paths]
            entries = set(column)

            if len(entries) == 1:
                self.regexes.append(entries.pop())
                continue

            # Here we make a regex that match with most of the column's elements
            opac_regex = OPaCRegex(list(entries))
            regex = opac_regex.digest()
            self.regexes.append(regex)

            paths = [path for path in paths if re.match('^' + regex + '$', path[index])]

        self.regexes.reverse()
        return self.regexes

    '''
        Removes the branch's paths that match with the previous generated regexes
    '''
    def clean(self):
        if self.node.remove_path(self.regexes):
            tmp = {}
            self.node.parent.weight = 0
            for key, node in self.node.parent.children.iteritems():
                if not key == self.node.name:
                    tmp[key] = node
                    self.node.parent.weight += node.weight
            self.node.parent.children = tmp


''' ################################
        PRIVATE - PATHNODE CLASS
    ################################
'''
class PathNode:

    def __init__(self, name, parent=None, depth=0, weight=1):
        self.children = {}
        self.parent = parent
        self.name = name
        self.depth = depth
        self.weight = weight

        self.same_depth = 0

    '''
        This method calculates the expectation and deviation respect the children
        nodes' weights
    '''
    def distribution(self):
        weights  = [child.weight for name, child in self.children.iteritems()]

        expectation = sum(weights)/float(len(weights))
        variance    = sum([math.pow((weight - expectation), 2) for weight in weights])/len(weights)
        deviation   = math.sqrt(variance)

        return (expectation, deviation)


    '''
        Generates all the paths for an specified depth
    '''
    def paths_per_depth(self, depth, path=[]):
        _path = path + [self.name]

        paths = []
        if (self.depth == depth) and not self.children:
            paths = [_path]
        elif self.depth < depth:
            for name, child in self.children.iteritems():
                paths.extend(child.paths_per_depth(depth, _path))

        return paths


    '''
        Returns the total weights for every depth in the branch
    '''
    def _weight_per_depth(self, depths={}):
        _depths = depths.copy()
        if not self.children:
            if not self.depth in _depths:
                _depths[self.depth] = 0

            _depths[self.depth] += 1
        else:
            for child in self.children:
                _depths = self.children[child]._weight_per_depth(_depths)

        return _depths


    ''' 
        Generates one Scrap instance for each branch that we have to process
    '''
    def get_scrap(self, weight):
        scrap = []

        depths = self._weight_per_depth()
        for depth, depth_weight in depths.iteritems():
            if depth_weight >= weight:
                scrap.append(Scrap(self, depth, depth_weight))

        return scrap


    ''' 
        Returns nodes that are heavier than the especified weight
    '''
    def heaviers(self, weight):
        return [child for name, child in self.children.iteritems() if child.weight > weight]


    '''
        Adds a new path into the tree.
    '''
    def add_path(self, path):

        child_name = path[0]

        if child_name in self.children:
            self.weight += 1
        else:
            if self.children:
                self.weight += 1
            self.children[child_name] = PathNode(child_name, self, self.depth+1)

        if len(path) > 1:
            self.children[child_name].add_path(path[1:])


    '''
        Removes all the entries in the branch that match with the specified
        list of regexes.
    '''
    def remove_path(self, path_regexes):

        if not path_regexes:
            return False

        if re.match('^' + path_regexes[0] + '$', self.name):

            if self.children and (len(path_regexes) > 1):
                children = {}
                self.weight = 0
                for name, child in self.children.iteritems():
                    if child.remove_path(path_regexes[1:]) and not child.children:
                        continue

                    self.weight += child.weight
                    children[name] = child

                self.children = children
            return True

        return False


    '''
        Is the branch empty
    '''
    def is_empty(self):
        return not bool(self.children)


    '''
        Prints the tree. Just for debugging uses
    '''
    def print_tree(self, depth=-1):
        print "----|"*self.depth + self.name + "({0} - {1} #({2}))".format(self.depth,
                                                                               self.weight,
                                                                               len(self.children))
        
        for child in self.children:
            self.children[child].print_tree(depth)


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
        self.tree = PathNode('', weight=0)

        self.previous_weight = 0
        self.trigger_weight  = 30

        self.takenA = 0
        self.takenB = 0


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
            for _sfilter, (_cfilter, entries) in self.filters.iteritems():
                if _cfilter.match(path):
                    if entries:
                        self.filters[_sfilter] = (_cfilter, entries - 1)
                        self.paths.add(path)
                        return True
                    return False
            self.tree.add_path(spath)
            self.paths.add(path)
            return True

        return False

    '''

    '''
    def update(self, paths):

        for path in paths:
            self.add_path(path)

        if self.size() > self.trigger_weight:

            now = self.size()
            self.clean()
            self.previous_weight = self.size()

            direct = '^'
            if self.takenA <= self.takenB:
                self.trigger_weight += 30
            else:
                direct = 'v'

            print '[WEIGHTS] Trigg: {0} - Act: {1} - Post: {2} - Taken: {3}'.format(self.trigger_weight,
                                                                       now,
                                                                       self.previous_weight,
                                                                       direct)

            self.trigger_weight = self.size() + 30

            self.takenB = self.takenA
            self.takenA = 0


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

