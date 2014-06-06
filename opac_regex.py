import re


class OPaCRegexNode:
    def __init__(self, first_value):
        self.occurrences = [first_value]

    def fuse(self, node, way):
        self.occurrences = way(self.occurrences, node.occurrences)

    def quantifier(self):
        #print self.occurrences
        qs = list(set(self.occurrences))
        qs.sort()
        weight = len(qs)
        if weight > 2:
            return '+'
        elif weight == 2:
            return '{{{0},{1}}}'.format(qs[0], qs[1])
        elif qs[0] == 1:
            return ''
        else:
            return '{{{0}}}'.format(qs[0])

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

    def render(self):
        result = '('
        for node in self.nodes:
            result += node.render()
        result += ')'
        return result + self.quantifier()


    def compress(self):
        size = 2
        index = 0
        while (len(self.nodes)/size) > 1:

            chunks = [self.nodes[i:i+size] for i in range(index, len(self.nodes), size)]

            tail = []
            if len(chunks[-1]) != size:
                tail = chunks[-1]
                chunks = chunks[:-1]

            #print 'chunks: {0} - size: {1} - index: {2}'.format(len(chunks), size, index)

            #######################################################
            _nodes = [OPaCRegexInnerNode(chunk) for chunk in chunks]

            first_node = _nodes[0]
            compressed = self.nodes[:index]
            merging = False
            for node in _nodes[1:]:
                if first_node == node:
                    first_node.fuse(node, lambda l1, l2 : l1 + l2)
                    merging = True
                else:
                    if merging:
                        compressed.append(first_node)
                    else:
                        compressed.extend(first_node.nodes)
                    merging = False
                    first_node = node

            if merging:
                compressed.append(first_node)
            else:
                compressed.extend(first_node.nodes)

            #######################################################

            compressed.extend(tail)

            if len(self.nodes) > len(compressed):
                self.nodes = compressed
            elif len(self.nodes) >= (index + 2*size):
                index += 1
            else:
                size += 1


class OPaCRegexLeafNode(OPaCRegexNode):
    def __init__(self, value, length):
        OPaCRegexNode.__init__(self, length)
        self.value = value

    def key(self):
        return self.value

    def render(self):
        return self.value + self.quantifier()


class OPaCRegex:
    def __init__(self, entries):
        self.entries = entries
        self.tree = None


    def digest(self):
        opac_regexes = {}
        for entry in self.entries:
            elements = re.findall('(\d+|[^\W_]+|[\W_])', entry)

            #print entry
            last_node = None
            opac_regex = OPaCRegexInnerNode()
            for element in elements:
                first_c = element[0]
                if re.match('\d', first_c):
                    node = OPaCRegexLeafNode('\d', len(element))

                elif re.match('[^\W_]', first_c):
                    node = OPaCRegexLeafNode('[^\W_]', len(element))

                else:
                    node = OPaCRegexLeafNode('\\' + first_c, 1)
                    if last_node and (last_node == node):
                        last_node.fuse(node, lambda l1, l2 : [l1[0] + l2[0]])
                        continue
                last_node = node
                opac_regex.add_node(node)
            
            #print '*'*20
            opac_regex.compress()
            #print '[+] compressed: {0}'.format(opac_regex)
            
            regex_key = opac_regex.key()
            if regex_key in opac_regexes:
                opac_regexes[regex_key].fuse(opac_regex, lambda l1, l2: l1 + l2)
            else:
                opac_regexes[regex_key] = opac_regex

        print 'total = {0}'.format(len(self.entries))
        performance = {'$.+^':0}
        best_regex = '$.+^'
        for key, node in opac_regexes.iteritems():

            result = '^'
            result += node.render()
            result += '$'

            if result not in performance:
                performance[result] = 0
            
            for entry in self.entries:
                if re.match(result, entry):
                    performance[result] += 1

            if performance[best_regex] < performance[result]:
                best_regex = result

        print 'regex = {0} - {1}'.format(best_regex, performance[best_regex])
            


