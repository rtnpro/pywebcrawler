# -*- coding: utf-8 -*-

from __future__ import absolute_import
import json
from Queue import Queue


class StorageLoadException(Exception):
    pass


class StorageDumpException(Exception):
    pass


class BaseStorageBackend(object):
    """
    Base class for storage backends. This class can be extended to
    support different storage backends like sqlite, JSON, etc.
    """

    def __init__(self, root_url, storage_name):
        """
        Initialize storage backend.

        Args:
            root_url: A URL string
            storage_name: A string for the name of the storage, e.g.,
                a filename, or a database name, etc.
        """
        self.root_url = root_url
        self.storage_name = storage_name

    def load(self):
        """
        Load data from storage backend.
        """
        raise NotImplementedError

    def dump(self, urls_visited, queue, urls_count, urls_visited_count):
        """
        Dump data into the storage backend.
        """
        raise NotImplementedError


class JSONStorageBackend(BaseStorageBackend):
    """
    JSON storage backend for storing crawler data.
    """

    def get_data_dict(self):
        """
        Get data dictionary from specified storage.
        """
        try:
            f = open(self.storage_name)
            data = json.load(f)
            f.close()
            return data
        except Exception as e:
            raise StorageLoadException(unicode(e))

    def load(self):
        """
        Load data from the storage backend.

        Returns:
            A tuple: (urls_visited, urls_queued, queue, urls_count,
                      urls_visited_count)
            where
                urls_visited: A set of visited URL strings.
                urls_queued: A set of queued URL strings.
                queue: A Queue instance containing the crawler queue.
                urls_count: An integer for total URLs found.
                urls_visited_count: An integer for count of visited URLs.

        Raises:
            StorageLoadException
        """
        data_dict = self.get_data_dict()
        root_url = data_dict.get('root_url')
        if root_url != self.root_url:
            raise StorageLoadException(
                "Current root URL does not match with the one in the storage "
                "file.")
        urls_visited = set(data_dict.get('urls_visited', []))
        queue_data = data_dict.get('queue_data', [])
        urls_queued = set()
        urls_count = data_dict.get('urls_count', 1)
        urls_visited_count = data_dict.get('urls_visited_count', 0)
        queue = Queue()
        for item in queue_data:
            queue.put(item)
            urls_queued.add(item[0])
        return (urls_visited, urls_queued, queue, urls_count,
                urls_visited_count)

    def dump(self, urls_visited, queue, urls_count, urls_visited_count):
        """
        Dump data into the JSON storage backend.

        Args:
            urls_visited: A set of visited URL strings.
            queue: A Queue instance containing the crawler queue.
            urls_count: An integer for total URLs found.
            urls_visited_count: An integer for count of visited URLs.

        Raises:
            StorageDumpException
        """
        try:
            queue_data = []
            while not queue.empty():
                queue_data.append(queue.get())
            data_dict = {
                'root_url': self.root_url,
                'urls_visited': list(urls_visited),
                'queue_data': queue_data,
                'urls_count': urls_count,
                'urls_visited_count': urls_visited_count
            }
            f = open(self.storage_name, 'w')
            json.dump(data_dict, f, indent=2)
            f.close()
        except Exception as e:
            raise StorageDumpException(unicode(e))
