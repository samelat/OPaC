import re
import sys
import time
import urllib
import urllib2
import urlparse
from lxml import etree

from opac import OPaC

if len(sys.argv) < 2:
	print './test <url>'
	sys.exit(-1)
domain = sys.argv[1]

def get_paths(uri):
	paths = []
	try:
		data = urllib2.urlopen(uri).read()

		tree = etree.HTML(data)

		for element in tree.findall('.//a[@href]'):
			href = element.attrib['href']
			_uri = urlparse.urljoin(uri, href)

			paths.append(urllib.quote(urlparse.urlsplit(_uri).path))
	except:
		return []
	return paths

container = OPaC()
paths = get_paths(domain)
for path in paths:
	container.add_path(path)

begin = time.time()

count = 0
requests_count = 0
last_size = 0
for path in container:

	uri = urlparse.urljoin(domain, path)
	requests_count += 1
	print '[URI({0})] {1}'.format(requests_count, uri)

	paths = get_paths(uri)
	for path in paths:
		container.add_path(path)

	if (container.size() - last_size) > 200:
		container.clean()
		count = 0
		last_size = container.size()
	else:
		count += 1

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