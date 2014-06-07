import re
import sys
import math
import string

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

    def __str__(self):
        return '[{0}] {1} | {2}'.format(self.node.name, self.depth, self.weight)

    def get_filter(self):

        regexes = []
        paths = self.node.paths_per_depth(self.depth)

        print '#'*20

        for path in paths:
            print path

        _filter = ''
        for index in range(0, self.depth):
            column = [path[index] for path in paths]
            entries = set(column)

            if len(entries) == 1:
                regexes.append(entries.pop())
                continue

            # Armamos una expresion regular que contemple el mayor numero
            # de elementos en la columna
            opac_regex = OPaCRegex(list(entries))
            regexes.append(opac_regex.digest())

        _filter =  '^' + '/'.join(regexes) + '$'

        count = 0
        print _filter
        for path in paths:
            if re.match(_filter, '/'.join(path)):
                count += 1

        print 'performance: {0}/{1}'.format(count, len(paths))


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


    '''
        Genera todos los paths existentes en el arbol para una profundidad
        establecida.
    '''
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
        Add a new path into the tree.
        Return False if the path already exists.
    '''
    def add_path(self, path):

        root = path[0]
        w_value = True

        if root in self.children:
            w_value = False
        else:
            self.children[root] = PathNode(root, self, self.depth+1)

        if len(path) > 1:
            w_value = self.children[root].add_path(path[1:])
                
        if w_value:
            self.weight += 1

        return w_value

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
        self.limit_per_filter_entry = 4
        self.paths = []
        self.filters = {}
        self.tree = PathNode('')

    def __iter__(self):
        return self

    def next(self):
        if not self.paths:
            raise StopIteration
        else:
            return self.paths.pop(random.randint(0, len(self.paths)))

    def add_path(self, path):
        if self.tree.add_path(path):
            for _filter, entries in self.filters.iteritems():
                if _filter.match(path):
                    if entries:
                        self.filters[_filter] -= 1
                        break
                    return
            self.paths.append(path)

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

        '''
            Cambiar las claves de self.filters por los strings, porque sino, cuando
            busquemos si la regex ya esta creada, nunca la va a encontrar (todas las
            instancias de re.compile son diferentes).
            Meter todas las regex generadas por los scraps en una lista y estando
            compiladas, recien ahi iterar la lista. Creo que puede ser mas eficiente.
        '''
        for _scrap in scrap:
            _filter = _scrap.get_filter()
            _filter = re.compile(_filter)
            if _filter not in self.filters:
                self.filters[_filter] = self.limit_per_filter_entry
            print '------------------------------------------------------------'

            survivor_paths = filter(_filter.match, self.paths)


fd = open(sys.argv[1], 'r')
uris = fd.readlines()
fd.close()

paths = [uri.strip().split('/')[3:] for uri in uris]
paths = [[sdir for sdir in path if sdir] for path in paths]
paths = [path for path in paths if path]

opac = OPaC()
for path in paths:
    opac.add_path(path)

opac.clean()

