import re


class OPaCRegexNode:
    def __init__(self, first_value):
        self.occurrences = [first_value]

    def fuse(self, node, way):
        self.occurrences = way(self.occurrences, node.occurrences)

    # Two nodes are equal if they have the same sign
    def __eq__(self, node):
        return self.key() == node.key()

    def __str__(self):
        return str(self.key())


class OPaCRegexInnerNode(OPaCRegexNode):
    def __init__(self, nodes=[]):
        OPaCRegexNode.__init__(self, 1)
        self.nodes = []
        self.nodes.extend(nodes)

    def add_node(self, node):
        self.nodes.append(node)

    def key(self):
        return tuple([n.key() for n in self.nodes])

    def fuse(self, node, way):
        self.occurrences = way(self.occurrences, node.occurrences)
        for i in range(0, len(self.nodes)):
            self.nodes[i].fuse(node.nodes[i], way)

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

            nodes = [OPaCRegexInnerNode(chunk) for chunk in chunks]

            rest = nodes[0]
            compressed = []
            for node in nodes[1:]:

                if nodes[index] == nodes[index+1]:
                    nodes[index].fuse(nodes[index+1], lambda l1, l2 : [l1[0] + l2[0]])

                    rest = None
                else:
                    compressed.extend(nodes[index].nodes)
                    rest = nodes[index+1].nodes
            if rest:
                compressed.extend(rest)

            compressed.extend(tail)

            if len(self.nodes) > len(compressed):
                self.nodes = compressed
            else:
                size += 1


class OPaCRegexLeafNode(OPaCRegexNode):
    def __init__(self, value, length):
        OPaCRegexNode.__init__(self, length)
        self.value = value

    def key(self):
        return self.value


class OPaCRegex:
    def __init__(self, entries):
        self.entries = entries

        self.tree = None


    def digest(self):
        opac_regexes = {}
        for entry in self.entries:
            elements = re.findall('(\d+|[^\W_]+|[\W_])', entry)

            #print entry
            opac_regex = OPaCRegexInnerNode()
            for element in elements:
                first_c = element[0]
                if re.match('\d', first_c):
                    opac_regex.add_node(OPaCRegexLeafNode('\d', len(element)))
                    #_regex.append(('\d', [len(element)]))
                elif re.match('[^\W_]', first_c):
                    opac_regex.add_node(OPaCRegexLeafNode('[^\W_]', len(element)))
                    #_regex.append(('[^\W_]', [len(element)]))
                #elif _regex and (_regex[-1][0] == '\\' + first_c):
                    # Si existen dos ocurrencias del mismo simbolo,
                    #    incrementamos en 1 el numero de ocurrencias, sin
                    #    agregar un nuevo numero a la cantidad
                    #_regex[-1][1][0] += 1
                else:
                    opac_regex.add_node(OPaCRegexLeafNode('\\' + first_c, 1))
                    #_regex.append(('\\' + first_c, [1]))
            
            print '*'*20
            opac_regex.compress()
            print opac_regex
            
            regex_key = opac_regex.key()
            if regex_key in opac_regexes:
                opac_regexes[regex_key].fuse(opac_regex, lambda l1, l2: l1 + l2)
            else:
                opac_regexes[regex_key] = opac_regex


    def make_regex(self):
        
        pass


