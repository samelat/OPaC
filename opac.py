import sys
import math

''' ################################
        PRIVATE - SCRAP CLASS
    ################################
'''
class Scrap:
    def __init__(self, node, depth, weight):
        self.node   = node
        self.depth  = depth
        self.weight = weight

    def __str__(self):
        return '[{0}] {1} | {2}'.format(self.node.name, self.depth, self.weight)


    def make_regex(self, string):
        pass


    def get_filters(self):
        _filter = []

        paths = self.node.paths_per_depth(self.depth)

        for index in range(0, self.depth):
            column = [path[index] for path in paths]
            components = set(column)

            if len(components) == 1:
                _filter.append(components.pop())
                continue
            
            chars = {'digits': 0, 'letters':0, 'punctuation':0}
            for component in list(components):
                for char in component:
                    if char in chars:
                        chars[char] += 1
                    else:
                        chars[char]  = 1

            print chars


''' ################################
        PRIVATE - PATHNODE CLASS
    ################################
'''
class PathNode:

    def __init__(self, name, parent=None, depth=0):
        self.children = {}
        self.parent = parent
        self.name = name
        self.depth = depth

        self.same_depth = 0
        self.weight = 0

    ''' #######################################################################
        Este metodo calcula la esperanza y la desviacion estandar con respecto
        a los pesos de los nodos hijos.
    '''
    def distribution(self):
        weights  = [child.weight for name, child in self.children.iteritems()]

        expectation = sum(weights)/float(len(weights))
        variance    = sum([math.pow((weight - expectation), 2) for weight in weights])/len(weights)
        deviation   = math.sqrt(variance)

        return (expectation, deviation)


    def paths_per_depth(self, depth, path=[]):
        _path = path + [self.name]
        if self.depth == depth:
            paths = [_path]
        else:
            paths = []
            for name, child in self.children.iteritems():
                paths.extend(child.paths_per_depth(depth, _path))

        return paths


    ''' #######################################################################
        Devuelve el peso que hay para cada posible profundidad
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


    ''' #######################################################################
        Devuelve una instancia de scrap por cada path que haya que suprimir
    '''
    def get_scrap(self, weight):
        scrap = []

        depths = self._weight_per_depth()
        print depths
        for depth, depth_weight in depths.iteritems():
            if depth_weight >= weight:
                scrap.append(Scrap(self, depth, depth_weight))

        return scrap


    ''' #######################################################################
        Devuelve los nodos hijos cuyo peso es mayor al especificado
    '''
    def heaviers(self, weight):
        return [child for name, child in self.children.iteritems() if child.weight > weight]


    ''' #######################################################################
        Add a new path into the collection, filtering it if match with any
        expresion or if it was previously added.
    '''
    def add_path(self, path):

        self.weight += 1

        root = path[0]

        if root not in self.children:
            self.children[root] = PathNode(root, self, self.depth+1)

        if len(path) > 1:
            self.children[root].add_path(path[1:])

    ''' #######################################################################
        Obtenemos todo un subarbol, a partir de un path
    '''
    def get_node(self, path):
        subdirs = path.split('/')

        node = self
        for subdir in subdirs:
            if subdir == self.name:
                continue

            if subdir in node.children:
                node = node.children[subdir]
            else:
                break

        return node

    ''' #######################################################################

    '''
    def is_empty(self):
        return not bool(self.children)

    ''' #######################################################################

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
        self.tree = PathNode('')

    def add_path(self, path):
        self.tree.add_path(path)

    ''' #######################################################################
        Obtenemos todos los nodos que tienen claras caracteristicas que los
        hacen suprimibles.
    ''' 
    def clean(self):
        if self.tree.is_empty():
            return False

        weight_e, weight_devn = self.tree.distribution()

        print '[!] esperanza: {0} - desviacion: {1}'.format(weight_e, weight_devn)
        
        heavy_nodes = self.tree.heaviers(weight_e + weight_devn)

        scrap = []
        for node in heavy_nodes:
            _scrap = node.get_scrap(weight_e + weight_devn)
            scrap.extend(_scrap)

            for s in _scrap:
                s.get_filters()

        return scrap


fd = open(sys.argv[1], 'r')
uris = fd.readlines()
fd.close()

paths = [uri.strip().split('/')[3:] for uri in uris]
paths = [path for path in paths if [sdir for sdir in path if sdir]]

opac = OPaC()
for path in paths:
    opac.add_path(path)

opac.clean()

