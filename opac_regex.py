import re

class OPaCRegexNode:
    def __init__(self, nodes=[]):
        self.nodes = []
        self.nodes.extend(nodes)
        self.occurrences = [1]

    def add_node(self, node):
        self.nodes.append(node)

    def key(self):
        return tuple([n.key() for n in self.nodes])

    def __str__(self):
        return str(self.key())

    # Two nodes are equal if they have the same sign
    def __eq__(self, node):
        return self.key() == node.key()

    def fuse(self, node, way):
        way(self, node)
        for i in range(0, len(self.nodes)):
            self.nodes[i].fuse(node.nodes[i])

    def compress(self):
        size = 2
        while True:
            chunks = [self.nodes[i:i+size] for i in range(0, len(self.nodes), size)]

            tail = []
            if len(chunks[-1]) != size:
                tail = chunks[-1]
                chunks = chunks[:-1]

            print 'chunks: {0} - size: {1}'.format(len(chunks), size)
            if len(chunks) < 2:
                break

            nodes = [OPaCRegexNode(chunk) for chunk in chunks]
                
            compressed = []
            for node in nodes:
                if not (compressed and (compressed[-1] == node)):
                    compressed[-1].fuse(node, lambda x, y : (x.occurrences[0] += y.occurrences[0]))
                    compressed.append(node)
            compressed.extend(tail)

            if len(self.nodes) > len(compressed):
                self.nodes = compressed
            else:
                size += 1




class OPaCRegexLeaf:
    def __init__(self, value, length):
        self.value = value
        self.occurrences = [length]

    def key(self):
        return self.value

    def __str__(self):
        return '{0}'.format(self.value)

    def fuse(self, node):
        if self.key() == node.key():
            self.occurrences.extend(node.occurrences)
            return True
        return False


class OPaCRegex:
    def __init__(self, entries):
        self.entries = entries

        self.tree = None


    def digest(self):
        opac_regexes = {}
        for entry in self.entries:
            elements = re.findall('(\d+|[^\W_]+|[\W_])', entry)

            #print entry
            opac_regex = OPaCRegexNode()
            for element in elements:
                first_c = element[0]
                if re.match('\d', first_c):
                    opac_regex.add_node(OPaCRegexLeaf('\d', len(element)))
                    #_regex.append(('\d', [len(element)]))
                elif re.match('[^\W_]', first_c):
                    opac_regex.add_node(OPaCRegexLeaf('[^\W_]', len(element)))
                    #_regex.append(('[^\W_]', [len(element)]))
                #elif _regex and (_regex[-1][0] == '\\' + first_c):
                    # Si existen dos ocurrencias del mismo simbolo,
                    #    incrementamos en 1 el numero de ocurrencias, sin
                    #    agregar un nuevo numero a la cantidad
                    #_regex[-1][1][0] += 1
                else:
                    opac_regex.add_node(OPaCRegexLeaf('\\' + first_c, 1))
                    #_regex.append(('\\' + first_c, [1]))
            
            print '*'*20
            opac_regex.compress()
            print opac_regex
            
            regex_key = opac_regex.key()
            if regex_key in opac_regexes:
                opac_regexes[regex_key].fuse(opac_regex, lambda x, y: x.occurrences.extend(y.occurrences))

            else:
                opac_regexes[regex_key] = opac_regex


    def make_regex(self):
        
        pass


