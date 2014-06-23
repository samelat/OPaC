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
	except KeyboardInterrupt:
		sys.exit()
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
	if domain not in uri:
		continue

	requests_count += 1

	print '[URI({0})] {1}'.format(requests_count, uri)

	paths = get_paths(uri)
	
	container.update(paths)

end = time.time()

print 'seconds: {0}'.format(end - begin)