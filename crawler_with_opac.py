#!/usr/bin/python3

'''
    Under Construction!
'''

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
        
        response = requests.get(url, allow_redirects=False)
        if response.status_code in range(300, 309):
            location = parse.urljoin(url, response.headers['location'])
            print('[!] Status Code: {0} - Redirected to {1}'.format(response.status_code, location))
            # If the redirect is inside the same site ...
            if re.match('^' + url, location):
                paths.append(location)
            return paths

        if (response.status_code != 200):
            print('[E] Status code {0}'.format(response.status_code))
            if (response.status_code in error_pages):
                return paths
            else:
                error_pages.add(response.status_code)

        soup = BeautifulSoup(response.text)

        tag = soup.find('base')
        base_url = tag.attrs['href'].strip() if tag and tag.has_attr('href') else ''
        url = base_url if base_url else url

        tags = soup.find_all('a', href=True)
        #print('[URL] {0}'.format(url))
        for tag in tags:
            href = tag.attrs['href'].strip()
            #print('[HREF] {0}'.format(href))
            _url = parse.urljoin(url, href)
            #print('[NEWURL] {0}'.format(_url))
            _url = parse.unquote(_url)

            #if '//' in _url:
            #    print('[URL] {0}'.format(url))
            #    print('[TAG] {0}'.format(href))
            #    sys.exit()

            if re.match('^' + url, _url):
                paths.append(parse.urlsplit(_url).path)

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

    print('[URI({0}/{1})] {2}'.format(requests_count, container.size(), uri))

    paths = get_paths(uri)
    for path in paths:
        container.add_path(path)

end = time.time()

print('seconds: {0}'.format(end - begin))
