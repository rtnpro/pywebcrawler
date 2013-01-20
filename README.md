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
```python

>>>from pywebcrawler import webcrawler
>>>crawler = webcrawler.WebCrawler('https://github.com/', depth_limit=2, max_url_count=200)
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

```
