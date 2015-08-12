
import re
import math
from opac_regex import OPaCRegex

''' ################################
        PRIVATE - PATHNODE CLASS
    ################################
'''
class PathNode:

    def __init__(self, name, parent=None, depth=0, weight=1):
        self.name = name
        self.regexes = {}
        self.children = {}
        self.trigger = 5
        #self.parent = parent
        #self.name = name

        #self.same_depth = 0


    '''
        Adds a new path into the tree.
    '''
    def add_path(self, path):

        child_node = None
        child_name = path[0]

        child_result = False
        local_result = False

        if child_name in self.children:
            child_node = self.children[child_name]
        else:
            for regex, child in self.regexes.items():
                if re.match('^' + regex + '$', child_name):
                    child_node = child
                    break
                    
        if not child_node:
            local_result = True
            child_node = PathNode(child_name)
            self.children[child_name] = child_node

        if len(path) > 1:
            child_result = child_node.add_path(path[1:])

        if local_result:
            self.compress()

        return (local_result or child_result)


    def compress(self):
        if len(self.children) < self.trigger:
            return

        opac_regex = OPaCRegex(list(self.children.keys()))
        regex = opac_regex.digest()

        if regex:
            regex_node = PathNode(regex)
            self.regexes[regex] = regex_node

            paths = list(self.children.keys())
            for path in paths:
                if re.match('^' + regex + '$', path):
                    regex_node.merge(self.children[path])
                    del(self.children[path])
        else:
            self.trigger *= 2


    def merge(self, node):
        for path, child in node.children.items():
            if path in self.children:
                self.children[path].merge(child)

        for regex, child in node.regexes.items():
            if regex in self.children:
                self.regexes[regex].merge(child)

        self.compress()


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
    def print_tree(self, depth=0):
        print("----|"*depth + self.name + "(# of childs: {0}))".format(len(self.children)))
        
        for child in self.children:
            self.children[child].print_tree(depth+1)

        for child in self.regexes:
            self.regexes[child].print_tree(depth+1)



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