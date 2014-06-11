import re
import sys
import time
import urlparse
from lxml import etree

from opac import OPaC

import urllib2

domain = 'http://www.cert.unlp.edu.ar'
container = [domain]
ready = set(container)

begin = time.time()

while container:

	uri = container.pop(0)
	print uri

	try:
		data = urllib2.urlopen(uri).read()

		tree = etree.HTML(data)

		for element in tree.findall('.//a[@href]'):
			href = element.attrib['href']
			_uri = urlparse.urljoin(uri, href)
			if (_uri in ready) or (domain not in _uri):
				continue

			container.append(_uri)
			ready.add(_uri)
	except:
		continue

end = time.time()

print 'seconds: {0}'.format(end - begin)

'''
fd = open(sys.argv[1], 'r')
uris = fd.readlines()
fd.close()

paths = [urlparse.urlsplit(uri).path.strip() for uri in uris]

opac = OPaC()
for path in paths:
    opac.add_path(path)

first_len = len(opac.paths)
opac.clean()
last_len = len(opac.paths)

print '{0}/{1}'.format(last_len, first_len)
'''