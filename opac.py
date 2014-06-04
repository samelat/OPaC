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


    '''
    def compress_regex(self, items):
        result = items

        # Spliteamos los items en chunks de diferentes tamanios, que comparamos
        size = 2
        while True:
            
            # Si nacen menos de 2 chunks del tamanio propuesto, abandonamos el proceso
            chunks = [result[i:i+size] for i in range(0, len(result), size)]

            tail = []
            if len(chunks[-1]) != size:
                tail = chunks[-1]
                chunks = chunks[:-1]

            #print 'size = {0} | chucks = {1}'.format(size, len(chunks))
            if len(chunks) < 2:
                break

            _result = []

            first_chunk = chunks[0]
            for chunk in chunks[1:]:

                keys1 = [t[0] for t in first_chunk]
                keys2 = [t[0] for t in chunk]

                # Comparamos los elementos de los diferentes chunks
                keys = [keys1[i] for i in range(0, size) if keys1[i] == keys2[i]]

                # Si los elementos son los mismos entre los chunks, los juntamos
                if len(keys) == size:
                    for i in range(0, size):
                        first_chunk[i][1].extend(chunk[i][1])
                else:
                    _result.extend(first_chunk)
                    first_chunk = chunk

            _result.extend(first_chunk)
            _result.extend(tail)

            #print '[!] _result: {0}'.format(_result)

            if len(_result) == len(result):
                size += 1

            result = _result

        #print '__result: {0}'.format(result)
        #print '------------------------------------------------------'
        return result


    def make_regex(self, entries):

        regex_info = {}
        for entry in entries:
            elements = re.findall('(\d+|[^\W_]+|[\W_])', entry)

            _regex = []
            for element in elements:
                first_c = element[0]
                if re.match('\d', first_c):
                    _regex.append(('\d', [len(element)]))
                elif re.match('[^\W_]', first_c):
                    _regex.append(('[^\W_]', [len(element)]))
                elif _regex and (_regex[-1][0] == '\\' + first_c):
                    # Si existen dos ocurrencias del mismo simbolo,
                    #    incrementamos en 1 el numero de ocurrencias, sin
                    #    agregar un nuevo numero a la cantidad
                    _regex[-1][1][0] += 1
                else:
                    _regex.append(('\\' + first_c, [1]))

            __regex = self.compress_regex(_regex)
            # print '{1} - {0}'.format(entry, __regex)

            regex_key = tuple([t[0] for t in __regex])
            if regex_key not in regex_info:
                regex_info[regex_key] = {}
                for key in regex_key:
                    regex_info[regex_key][key] = set([])

            for element, values in __regex:
                regex_info[regex_key][element].update(values)

        regexes = {}
        for regex_key in regex_info:
            regex = '^'
            for element in regex_key:
                quantifier = ''
                values = list(regex_info[regex_key][element])
                values.sort()
                if len(values) == 1:
                    quantifier = '{{{0}}}'.format(values[0])
                elif len(values) == 2:
                    quantifier = '{{{0},{1}}}'.format(*values)
                else:
                    quantifier = '+'
                regex += element + quantifier
            regex += '$'

            regexes[regex] = 0


        for entry in entries:
            for regex in regexes:
                if re.match(regex, entry):
                    regexes[regex] += 1

        print entries
        print 'total = {0}'.format(len(entries))
        for regex in regexes:
            print '{0} - {1}'.format(regex, regexes[regex])

        return regex
    '''


    def get_filters(self):
        regexes = []

        paths = self.node.paths_per_depth(self.depth)

        #for path in paths:
        #    print path

        for index in range(0, self.depth):
            column = [path[index] for path in paths]
            entries = set(column)

            if len(entries) == 1:
                regexes.append(entries.pop())
                continue
            
            print '#'*10 + '({0})'.format(index) + '#'*10

            # Armamos una expresion regular que contemple el mayor numero
            # de elementos en la columna
            opac_regex = OPaCRegex(list(entries))
            opac_regex.digest()

        print regexes


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
        Add a new path into the collection, filtering it if match with any
        expresion or if it was previously added.
    '''
    def add_path(self, path):

        root = path[0]
        w_value = True

        if root not in self.children:
            self.children[root] = PathNode(root, self, self.depth+1)
        else:
            w_value = False

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

        for _scrap in scrap:
            _scrap.get_filters()
            print '------------------------------------------------------------'

        return scrap


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

