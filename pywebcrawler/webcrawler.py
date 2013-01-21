# -*- coding: utf-8 -*-

from __future__ import absolute_import
import sys
import urllib2
import urlparse
from . import conf
from . import storage
from Queue import Queue
from BeautifulSoup import BeautifulSoup


class StopCrawlingException(Exception):
    pass


class UrlFetch(object):
    """
    Fetch urls from a page at the given URL.
    """

    def __init__(self, url):
        self.url = url

    def should_ignore(self, data):
        """
        Whether data should be ignored or not.

        Args:
            data: An addinfourl instance

        Returns:
            A boolean, True if data should be ignored, else False.
        """
        mimetype = data.info().gettype()
        if mimetype not in conf.ACCEPT_MIMETYPES:
            print >> sys.stderr, (
                "Ignoring content from %s because it's mimetype: %s is not "
                "in %s." % (self.url, mimetype, conf.ACCEPT_MIMETYPES))
            return True
        return False

    def get_content_at_url(self):
        """
        Get content from the page at self.url.

        Returns:
            A unicode for the page's content. In case of any error,
            it returns None.
        """
        try:
            request = urllib2.Request(self.url)
            request.add_header("User-Agent", conf.USER_AGENT)
            handle = urllib2.build_opener()
        except IOError as e:
            print >> sys.stderr, (
                "There was an error opening page at %s. Error was:\n%s"
                % (self.url, unicode(e)))
            return None
        try:
            data = handle.open(request)
        except urllib2.HTTPError as e:
            print >> sys.stderr, (
                "There was an error opening page at %s. Error was:\n%s"
                % (self.url, unicode(e)))
            return None
        except urllib2.URLError as e:
            print >> sys.stderr, (
                "There was an error opening page at %s. Error was:\n%s"
                % (self.url, unicode(e)))
            return None
        if self.should_ignore(data):
            return None
        content = unicode(data.read(), "utf-8", errors="replace")
        return content

    def parse_links_from_content(self, content):
        """
        Parses all links from anchor tags in content.

        Args:
            content: Unicode text.

        Returns:
            A set of urls in tha page.
        """
        soup = BeautifulSoup(content)
        anchors = soup.findAll('a')
        urls = set()
        for anchor in anchors:
            href = anchor.get('href')
            if href is not None:
                urls.add(urlparse.urljoin(self.url, href))
        return urls

    def get_urls(self):
        """
        Get all urls in a page at self.url.

        Returns:
            A set of urls.
        """
        urls = set()
        content = self.get_content_at_url()
        if content:
            urls = self.parse_links_from_content(content)
        return urls


class WebCrawler(object):
    """
    Web crawler
    """

    URLFetchClass = UrlFetch

    def __init__(self, root, depth_limit=None, max_urls_count=None,
                 allowed=[], exclude=[]):
        """
        Initialize WebCrawler instance.

        Args:
            root: A URL string.
            depth_limit: An integer for the maximum depth to traverse from
                the root URL node.
            max_urls_count: An integer for the maximum number of URLs the
                crawler should discover.
            allowed: A list of allowed URL prefixes.
            exclude: A list of excluded URL prefixes.
        """
        self.set_depth_limit(depth_limit)
        self.set_max_urls_count(max_urls_count)
        self.set_root(root)
        self.allowed_url_prefixes = allowed or []
        self.excluded_url_prefixes = exclude or []

    def set_depth_limit(self, depth_limit):
        """
        Set the maximum depth to traverse from root URL during crawling.

        Args:
            depth_limit: An integer representing the maximum depth to
                traverse from the root.
        """
        return depth_limit if depth_limit is not None \
            else conf.DEPTH_LIMIT

    def set_max_urls_count(self, max_urls_count):
        """
        Set the maximum number of URLs to discover during crawling.

        Args:
            max_urls_count: An integer for the maximum number of URLs
                to discover during crawling.
        """
        self.max_urls_count = max_urls_count if max_urls_count is not None \
            else conf.MAX_URLS_COUNT

    def set_root(self, root):
        """
        Set the root URL for the crawling operation. This method also resets
        other related data like the URL queue, sets of urls visited and seen
        and their counts.

        Args:
            root: A URL string.
        """
        self.queue = Queue()
        self.queue.put((self.clean_url(root), 0))
        self.root_url = self.clean_url(root)
        self.url_fetch = self.URLFetchClass(self.root_url)
        self.urls_visited = set()
        self.urls_queued = set([root])
        self.urls_visited_count = 0
        self.urls_count = 1
        self.can_dump = True

    def clean_url(self, url):
        """
        Clean up fragments in an URL.

        Args:
            url: A URL string.

        Returns:
            A URL string without any fragments.
        """
        return urlparse.urldefrag(url)[0]

    def check_depth(self, depth):
        """
        Check if the current depth from root is allowed for crawling.

        Raises:
            StopCrawlingException: if current depth is greater than maximum
                allowed depth from root.
        """
        if depth > conf.DEPTH_LIMIT:
            raise StopCrawlingException(
                "Current depth %d from root node is greater than maximum "
                "allowed depth %d." % (depth, conf.DEPTH_LIMIT))

    def is_url_prefix_allowed(self, url):
        """
        Check if url prefix is allowed.

        Args:
            url: A URL string.

        Returns:
            A boolean.
        """
        for prefix in self.allowed_url_prefixes:
            if not url.startswith(prefix):
                return False
        return True

    def is_url_prefix_excluded(self, url):
        """
        Check if url prefix is excluded.

        Args:
            url: A URL string.

        Returns:
            A boolean.
        """
        for prefix in self.excluded_url_prefixes:
            if url.startswith(prefix):
                return True
        return False

    def should_queue_url(self, url):
        """
        Whether should queue a url.

        Args:
            url: A URL string.

        Returns:
            A boolean, True if url should be queued else False.
        """
        if self.urls_count + 1 > self.max_urls_count:
            raise StopCrawlingException(
                "Already found %d URLs." % self.max_urls_count)
        return (
            self.is_url_prefix_allowed(url) and
            not self.is_url_prefix_excluded(url) and
            url not in self.urls_visited and
            url not in self.urls_queued
        )

    def visit_url(self, url, depth):
        """
        Fetch data from 'url' and process data. By processing data, it means
        retrieving URLs from the data and queuing the newly found URLs along
        with their depth value if necessary.

        Args:
            url: A URL string.
            depth: An integer representing the current depth of 'url'
                from root.
        """
        self.url_fetch.url = url
        urls = self.url_fetch.get_urls()
        child_depth = depth + 1
        self.check_depth(child_depth)
        for u in urls:
            if self.should_queue_url(u):
                self.queue.put((self.clean_url(u), child_depth))
                self.urls_queued.add(u)
                self.urls_count += 1
        # Only if all the filtered URLs in a page are successfully queued,
        # then we mark this url as visited.
        try:
            self.urls_queued.remove(url)
        except KeyError:
            pass
        self.urls_visited.add(url)
        self.urls_visited_count += 1

    def crawl(self):
        """"
        The main crawler method. It just retrieves an item (URL, depth) from
        self.queue and visits the URL.
        """
        try:
            while not self.queue.empty():
                url, depth = self.queue.get()
                print >> sys.stderr, (
                    "Visiting URL '%s' at depth %d." % (url, depth))
                self.visit_url(url, depth)
        except StopCrawlingException as e:
            print >> sys.stderr, (
                "Stopping crawling. Reason was:\n %s" % unicode(e))
        finally:
            self.show_stats()

    def show_stats(self):
        print >> sys.stdout, (
            "==========\n"
            "STATISTICS\n"
            "==========\n"
            "URLs found: %(urls_found)s\n"
            "URLs visited: %(urls_visited)s\n"
            % {
                'urls_found': self.urls_count,
                'urls_visited': self.urls_visited_count}
        )

    def iter_urls(self):
        """
        Return an iterator for all unique URLs discovered so far.

        Returns:
            A iterator of URL strings.
        """
        return iter(self.urls_queued.union(self.urls_visited))

    def reset(self):
        """
        Reset crawler data.
        """
        self.urls_visited = set()
        self.urls_queued = set()
        self.urls_visited_count = 0
        self.urls_count = 0
        self.can_dump = False

    def dump(self, storage_backend):
        """
        Dump data collected during crawling to a storage backend.

        Args:
            storage_backend: An instance of
                'pywebcrawler.storage.BaseStorageBackend' or its subclass.
        """
        if self.can_dump:
            try:
                storage_backend.dump(
                    self.urls_visited, self.queue, self.urls_count,
                    self.urls_visited_count)
                self.reset()
            except storage.StorageDumpException as e:
                print >> sys.stderr, (
                    "Error during dumping crawler data:\n%s" % unicode(e))

    def load(self, storage_backend):
        """
        Load existing crawling data from a storage backend.

        Args:
            storage_backend: An instance of
                'pywebcrawler.storage.BaseStorageBackend' or its subclass.
        """
        try:
            (
                self.urls_visited, self.urls_queued,
                self.queue, self.urls_count, self.urls_visited_count
            ) = storage_backend.load()
            self.can_dump = True
        except storage.StorageLoadException as e:
            print >> sys.stderr, (
                "Error during loading crawler data, so resorting to "
                "initial data:\n%s" % unicode(e))
