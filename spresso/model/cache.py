import os
import time
from tempfile import mkstemp

from spresso.model.base import SettingsMixin


class CacheEntry(object):
    def __init__(self, lifetime, in_memory):
        self.timestamp = time.time()
        self.lifetime = lifetime
        self.in_memory = in_memory
        self.data = None
        self.data_file = None

    @property
    def valid(self):
        timestamp = time.time()
        return timestamp - self.timestamp < self.lifetime

    def set_data(self, data):
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
    cache = {}

    def set(self, handle, settings, data):
        in_memory = settings.in_memory
        lifetime = settings.lifetime

        if lifetime > 0:
            entry = CacheEntry(lifetime, in_memory)
            entry.set_data(data)
            self.cache.update({
                handle: entry
            })

    def get(self, handle):
        entry = self.cache.get(handle)
        if entry is not None:
            return entry.get_data()
        return None

    def flush(self):
        self.cache.clear()
