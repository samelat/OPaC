import sys
import urllib
from urllib.parse import urlsplit

from opac import OPaC

fd = open(sys.argv[1], 'r')
uris = fd.readlines()
fd.close()

paths = [urlsplit(uri).path.strip() for uri in uris]

opac = OPaC()
for path in paths:
    opac.add_path(path)

for tree in opac.trees.values():
    print('*'*64)
    tree.print_tree()
