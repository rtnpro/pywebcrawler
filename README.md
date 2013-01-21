pywebcrawler
============
A simple web crawler written in Python.

Installation
------------
1. Clone repository: ``git clone https://github.com/rtnpro/pywebcrawler.git``
1. Change directory: ``cd pywebcrawler``
1. Run setup: ``sudo python setup.py develop``

Usage
-----
### API

```python

>>>from pywebcrawler import webcrawler
>>>root_url = 'https://github.com/'
>>>crawler = webcrawler.WebCrawler(root_url, depth_limit=2, max_urls_count=200)
>>>crawler.crawl()
Stopping crawling. Reason was:
Already found 200 URLs.
==========
STATISTICS
==========
URLs found: 200
URLs visited: 15
>>>for url in crawler.iter_urls():
    # do something
    print url
    ....
    ....
>>># dump results
>>>from pywebcrawler.storage import JSONStorageBackend
>>>s = JSONStorageBackend(root_url, 'path/to/output.json')
>>>crawler.dump(s)
>>># loading data from a storage file
>>>crawler.load(s)
>>># Now you are good to continue crawling from where you left :)

```

### Command line

1. ``crawler.py http://python.org -d 3 -n 1000 -s output.json``
