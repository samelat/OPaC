import re
import math
from opac_regex import OPaCRegex

''' ################################
        PRIVATE - PATHNODE CLASS
    ################################
'''
class PathNode:

    def __init__(self, name):
        self.name = name
        self.regexes = {}
        self.children = {}
        self.trigger = 8


    ''' Adds a new path into the tree.
    '''
    def add_path(self, path):

        child_node = None
        child_name = path[0]

        child_change = False
        local_change = False

        if child_name in self.children:
            child_node = self.children[child_name]
 
        else:
            for regex, child in self.regexes.items():
                if re.match(regex, child_name):
                    child_node = child
                    break
                    
        if not child_node:
            local_change = True
            child_node = PathNode(child_name)
            self.children[child_name] = child_node

        if len(path) > 1:
            child_change = child_node.add_path(path[1:])

        if local_change:
            self.compress()

        return (local_change or child_change)


    def compress(self):
        if len(self.children) < self.trigger:
            return

        children_names = list(self.children.keys())

        opac_regex = OPaCRegex()
        regex = opac_regex.digest(children_names)

        matching_children = [child_name for child_name in children_names if re.match(regex, child_name)]

        # 0.7 is a totally arbitrary value (70% of strings, match)
        if (len(matching_children)/len(children_names)) > 0.7:

            regex_node = PathNode(regex)
            self.regexes[regex] = regex_node

            for child_name in matching_children:
                regex_node.merge(self.children[child_name])
                del(self.children[child_name])

            regex_node.compress()
        else:
            self.trigger = len(self.children) + 8


    def merge(self, node):
        for child_name, child_node in node.children.items():
            if child_name in self.children:
                self.children[child_name].merge(child_node)
                continue

            for regex in self.regexes:
                if re.match(regex, child_name):
                    self.regexes[regex].merge(child_node)
                    break

            self.children[child_name] = child_node

    '''
        Prints the tree. Just for debugging uses
    '''
    def print_tree(self, depth=0):
        print("----|"*depth + self.name + "(# of childs: {0})".format(len(self.children)))
        
        for child in self.children:
            self.children[child].print_tree(depth+1)

        for child in self.regexes:
            self.regexes[child].print_tree(depth+1)

