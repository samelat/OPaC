#!/usr/bin/python3

import re
import sys
import time
import urllib
import requests
from bs4 import BeautifulSoup
from urllib import parse

from opac import OPaC

if len(sys.argv) < 2:
    print('./test <url>')
    sys.exit(-1)
domain = sys.argv[1]

error_pages = set()

def get_paths(url):
    paths = []
    try:
        
        response = requests.get(url)
        current_url = response.url
        if not re.match('^' + url, current_url):
            print('[!] Redirected to {0}'.format(current_url))
            return []

        if (response.status_code != 200):
            if (response.status_code in error_pages):
                return []
            else:
                error_pages.add(response.status_code)

        soap = BeautifulSoup(response.text)

        tags = soap.find_all('a', href=True)
        for tag in tags:
            href = tag.attrs['href']
            _url = parse.urljoin(current_url, href)

            paths.append(parse.quote(parse.urlsplit(_url).path))

    except KeyboardInterrupt:
        sys.exit()
    #except:
    #    return []

    return paths

container = OPaC()
paths = get_paths(domain)
for path in paths:
    container.add_path(path)

begin = time.time()

count = 0
requests_count = 0
last_size = 0

print('[!] Starting ...')
for path in container:

    # Do not make requests out of domain
    uri = parse.urljoin(domain, path)
    if domain not in uri:
        continue

    try:
        response = requests.head(uri)
    except KeyboardInterrupt:
        break
    #except:
    #    continue
    
    # If we are not interested in the content type, we continue with
    # the next URI
    if 'text/html' not in response.headers['content-type']:
        continue

    requests_count += 1

    print('[URI({0}/{1})] {2}'.format(requests_count, len(container.paths), uri))

    paths = get_paths(uri)
    for path in paths:
        container.add_path(path)

end = time.time()

print('seconds: {0}'.format(end - begin))