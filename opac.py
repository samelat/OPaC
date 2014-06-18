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

    def get_regexes(self):

        paths = self.node.paths_per_depth(self.depth)

        #print '#'*20

        print '[PATHS]'
        for path in paths:
            print path

        if not paths:
            print '[ERROR] name: {0} - depth: {1}'.format(self.node.name, self.depth)
            #self.node.print_tree()
            1/0

        for index in range(self.depth - 1, -1, -1):
            column = [path[index] for path in paths]
            entries = set(column)

            if len(entries) == 1:
                self.regexes.append(entries.pop())
                continue

            # Armamos una expresion regular que contemple el mayor numero
            # de elementos en la columna
            opac_regex = OPaCRegex(list(entries))
            regex = opac_regex.digest()
            self.regexes.append(regex)

            paths = [path for path in paths if re.match('^' + regex + '$', path[index])]

        #if '$.+^' in regexes:
        #    print '[@@@@] {0}'.format(paths)

        self.regexes.reverse()
        return self.regexes

    def clean(self):
        if self.node.remove_path(self.regexes):
            tmp = {}
            for key, node in self.node.parent.children.iteritems():
                if not key == self.node.name:
                    tmp[key] = node
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
        Genera todos los paths existentes en el arbol de una profundidad
        establecida.
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
        print '[DEPTHS] ({0}) - {1}'.format(self.name, depths)
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
            return False

        if not re.match('^' + path_regexes[0] + '$', self.name):
            return False

        if self.children and (len(path_regexes) > 1):
            children = {}
            self.weight = 0
            for name, child in self.children.iteritems():
                if child.remove_path(path_regexes[1:]):
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
        return self.tree.weight

    def add_path(self, path):
        if (path in self.paths) or (path in self.saw_paths):
            return

        print '[PATH] "{0}"'.format(path)

        spath = path.strip('/').split('/')
        if spath:
            for _sfilter, (_cfilter, entries) in self.filters.iteritems():
                if _cfilter.match(path):
                    if entries:
                        self.filters[_sfilter] = (_cfilter, entries - 1)
                        self.paths.add(path)
                    print 'filtrado'
                    return
            self.tree.add_path(spath)
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

        for _scrap in scrap:
            print '[SCRAP] depth: {0}, root: {1}'.format(_scrap.depth, _scrap.node.name)

        survivor_paths = self.paths
        for _scrap in scrap:
            try:
                regexes = _scrap.get_regexes()
            except:
                raise ''

            _sfilter =  '^/' + '/'.join(regexes) + '/?$'

            print regexes
            print _sfilter
            _cfilter = re.compile(_sfilter)
            if _sfilter in self.filters:
                print '[!!!] NOOOO {0} - depth: {1} - name: {2}'.format(_sfilter, _scrap.depth, _scrap.node.name)
                _scrap.node.print_tree()
                1/0

            _scrap.clean()

            ################ DEBUG ###############
            # count = 0
            # for path in paths:
            #     if re.match(_filter, '/'.join(path)):
            #         count += 1
            # 
            # print 'performance: {0}/{1}'.format(count, len(paths))
            ######################################

            self.filters[_sfilter] = (_cfilter, self.limit_per_filter_entry)
            print '------------------------------------------------------------'
            #print survivor_paths
            _tmp = []
            for path in survivor_paths:
                if _cfilter.match(path):
                    self.saw_paths.add(path)
                else:
                    _tmp.append(path)
            survivor_paths = _tmp

        self.paths = set(survivor_paths)

