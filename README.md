pywebcrawler
============
A simple web crawler written in Python.

Installation
------------
`pip install -e git+git://github.com/rtnpro/pywebcrawler.git@master#egg=pywebcrawler`

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

```
