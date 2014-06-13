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

    def __str__(self):
        return '[{0}] {1} | {2}'.format(self.node.name, self.depth, self.weight)

    def get_regexes(self):

        regexes = []
        paths = self.node.paths_per_depth(self.depth)

        print '#'*20

        #for path in paths:
        #    print path

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

        return regexes


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

    ''' Eliminamos todas las entradas del arbol que matcheen con el
        filtro especificado.
    '''
    def remove_path(self, path_regexes):

        # print '[RGX]({0}) - {1}'.format(self.name, path_regexes)
        if not path_regexes:
            return True

        if self.children:
            children = {}
            self.weight = 0
            for name, child in self.children.iteritems():
                if re.match('^' + path_regexes[0] + '$', name) and child.remove_path(path_regexes[1:]):
                    continue

                self.weight += child.weight
                children[name] = child

            self.children = children

        # We ask again about the children
        if not self.children:
            return True

        return False

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

    def size(self):
        size = 0
        if self.children:
            for name, child in self.children.iteritems():
                size += child.size()
        else:
            return 1
        return size


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

    def __iter__(self):
        return self

    def next(self):
        if not self.paths:
            raise StopIteration
        else:
            path = self.paths.pop()
            self.saw_paths.add(path)
            return path

    def size(self):
        return len(self.paths)

    def add_path(self, path):
        if (path in self.paths) or (path in self.saw_paths):
            return

        spath = path.strip('/').split('/')
        if spath:
            self.tree.add_path(spath)
            for _sfilter, (_cfilter, entries) in self.filters.iteritems():
                if _cfilter.match(path):
                    if entries:
                        self.filters[_sfilter] = (_cfilter, entries - 1)
                        break
                    return
            self.paths.add(path)

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
        survivor_paths = self.paths
        for _scrap in scrap:
            regexes = _scrap.get_regexes()

            self.tree.remove_path(regexes)

            _sfilter =  '^/' + '/'.join(regexes) + '$'

            ################ DEBUG ###############
            # count = 0
            # for path in paths:
            #     if re.match(_filter, '/'.join(path)):
            #         count += 1
            # 
            # print 'performance: {0}/{1}'.format(count, len(paths))
            ######################################

            print _sfilter
            _cfilter = re.compile(_sfilter)
            if _sfilter not in self.filters:
                self.filters[_sfilter] = (_cfilter, self.limit_per_filter_entry)
            print '------------------------------------------------------------'
            #print survivor_paths
            survivor_paths = filter(lambda x: not bool(_cfilter.match(x)), survivor_paths)

        self.paths = set(survivor_paths)

