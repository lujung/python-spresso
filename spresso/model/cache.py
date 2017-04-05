import os
import time
from tempfile import mkstemp

from spresso.model.base import SettingsMixin


class CacheEntry(object):
    """A class to represent a cache entry. Provides methods to check its 
        validity, set data and get data."""

    def __init__(self, lifetime, in_memory):
        self.timestamp = time.time()
        self.lifetime = lifetime
        self.in_memory = in_memory
        self.data = None
        self.data_file = None

    @property
    def valid(self):
        """Validate the lifetime of a cache entry.
            
            Returns:
                bool: The validity.
        """
        timestamp = time.time()
        return timestamp - self.timestamp < self.lifetime

    def set_data(self, data):
        """Set data on a cache entry. The data can be saved in memory or as a 
            temporary file.
        
            Args:
                data(str): The data to be cached.
        """
        if self.in_memory:
            self.data = data
        else:
            data_fd, data_path = mkstemp()
            with open(data_path, 'w') as f:
                f.write(data)
            os.close(data_fd)

            if self.data_file is not None:
                os.remove(self.data_file)

            self.data_file = data_path

    def get_data(self):
        """Retrieve data from a cache entry, if the cache entry is valid. The 
            data is either loaded from memory or from the file system. 
            
            Returns:
                None or the cached data.
        """
        if not self.valid:
            return None

        if self.in_memory:
            return self.data
        else:
            if self.data_file is None:
                return None

            with open(self.data_file, 'r') as f:
                data = f.read()

            return data


class Cache(SettingsMixin):
    """Class to provide a central caching object. The object handles the caching
        settings and manages a dictionary of :class:`CacheEntry` instances."""
    cache = {}

    def set(self, handle, settings, data):
        """Create and store a :class:`CacheEntry`.
        
            Args:
                handle(str): The unique identifier.
                settings(:class:`CachingSetting`): The caching configuration.
                data(str): The data to be cached.
        """
        in_memory = settings.in_memory
        lifetime = settings.lifetime

        if lifetime > 0:
            entry = CacheEntry(lifetime, in_memory)
            entry.set_data(data)
            self.cache.update({
                handle: entry
            })

    def get(self, handle):
        """Retrieve cached data.
        
            Args:
                handle(str): The unique identifier.
            
            Returns:
                None or the cached data.
        """
        entry = self.cache.get(handle)
        if entry is not None:
            return entry.get_data()
        return None
