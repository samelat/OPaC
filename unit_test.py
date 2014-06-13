import sys
import urlparse

from opac import OPaC

fd = open(sys.argv[1], 'r')
uris = fd.readlines()
fd.close()

paths = [urlparse.urlsplit(uri).path.strip() for uri in uris]

opac = OPaC()
for path in paths:
    opac.add_path(path)

print 'WEIGHT: {0} - SIZE: {1}'.format(opac.tree.weight, opac.tree.size())

first_len = len(opac.paths)
opac.clean()
last_len = len(opac.paths)

print '{0}/{1}'.format(last_len, first_len)

print 'WEIGHT: {0} - SIZE: {1}'.format(opac.tree.weight, opac.tree.size())