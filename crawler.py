# -*- coding: utf-8 -*-
import sys
import optparse
from pywebcrawler.webcrawler import WebCrawler
from pywebcrawler.storage import JSONStorageBackend
from pywebcrawler.log import set_log_level

USAGE = '%prog URL [options]'
VERSION = '0.1'


def parse_options():
    """
    Parses any command line options.

    Returns:
        args, opts
    """
    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
                      default=False,
                      help="don't print status messages to stdout")

    parser.add_option("-d", "--depth", action="store", type="int", default=5,
                      dest="depth_limit", help="Maximum depth to traverse")

    parser.add_option("-n", "--number", action="store", type="int",
                      dest="max_urls_count", default=1000,
                      help="Maximum number of URLs to discover.")

    parser.add_option("-x", "--exclude", action="append", type="string",
                      dest="exclude", default=[],
                      help="Exclude URL with this prefix.")

    parser.add_option("-a", "--allowed", action="append", type="string",
                      dest="allowed", default=[],
                      help="Allow URL with this prefix.")

    parser.add_option("-s", "--storage", action="store", type="string",
                      dest="storage_name",
                      help="Name of storage, e.g., filename.")

    parser.add_option("-l", "--load", action="store_true", default=False,
                      dest="load", help=("Load initial data from storage "
                                         "if available."))

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if not opts.storage_name and opts.load:
        parser.print_help(sys.stderr)
        parser.error("options -l works only when option -s is set.")

    return opts, args


def main():
    opts, args = parse_options()

    root_url = args[0]

    depth_limit = opts.depth_limit
    max_urls_count = opts.max_urls_count
    exclude = opts.exclude
    allowed = opts.allowed
    load = opts.load
    storage_name = opts.storage_name

    # set log level
    set_log_level('DEBUG')
    if opts.quiet:
        set_log_level('WARNING')

    crawler = WebCrawler(root_url, depth_limit=depth_limit,
                         max_urls_count=max_urls_count, allowed=allowed,
                         exclude=exclude)
    if storage_name:
        storage = JSONStorageBackend(root_url, storage_name)
        if load:
            crawler.load(storage)
    crawler.crawl()
    if storage_name:
        crawler.dump(storage)

if __name__ == "__main__":
    main()
