import os
import unittest

from unittest.mock import patch, Mock

from spresso.model.cache import CacheEntry, Cache
from spresso.model.settings import CachingSetting


class CacheEntryTestCase(unittest.TestCase):
    def test_valid(self):
        lifetime = -5
        in_memory = True
        entry = CacheEntry(lifetime, in_memory)
        self.assertFalse(entry.valid)

        entry.lifetime = 0
        self.assertFalse(entry.valid)

        entry.lifetime = 5
        self.assertTrue(entry.valid)

    def test_set_data(self):
        lifetime = 5
        in_memory = True
        entry = CacheEntry(lifetime, in_memory)
        data = "test"
        entry.set_data(data)
        self.assertEqual(entry.data, data)

        entry.in_memory = False
        entry.set_data(data)
        with open(entry.data_file, 'r') as file:
            data_file = file.read()
        self.assertEqual(data_file, data)

        old_data_file = entry.data_file
        entry.set_data(data)
        self.assertFalse(os.path.isfile(old_data_file))

    def test_get_data(self):
        lifetime = -5
        in_memory = True
        entry = CacheEntry(lifetime, in_memory)
        self.assertEqual(entry.get_data(), None)

        lifetime = 50
        entry = CacheEntry(lifetime, in_memory)
        entry.data = "memory test"
        self.assertEqual(entry.get_data(), "memory test")

        entry.in_memory = False
        self.assertEqual(entry.get_data(), None)

        file_path = os.path.join(os.path.dirname(__file__), "test")
        with open(file_path, 'w') as file:
            file.write("file test")

        entry.data_file = file_path
        self.assertEqual(entry.get_data(), "file test")

        os.remove(file_path)


class CacheTestCase(unittest.TestCase):
    @patch("spresso.model.cache.CacheEntry")
    def test_set(self, cache_entry_mock):
        entry = Mock()
        cache_entry_mock.return_value = entry
        settings = Mock()

        cache = Cache(settings=settings)
        handle = "id"
        settings = CachingSetting(
            name="default",
            in_memory=True,
            lifetime=50
        )

        data = "test"
        cache.set(handle, settings, data)

        cache_entry_mock.assert_called_once_with(50, True)
        entry.set_data.assert_called_once_with(data)
        self.assertEqual(cache.cache['id'], entry)

    def test_get(self):
        settings = Mock()

        cache = Cache(settings=settings)
        self.assertIsNone(cache.get(None))

        entry = Mock()
        entry.get_data.return_value = "test"
        cache.cache.update(dict(id=entry))
        self.assertEqual(cache.get("id"), "test")
        self.assertEqual(entry.get_data.call_count, 1)
