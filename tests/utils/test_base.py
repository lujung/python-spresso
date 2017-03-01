import os
import string
import unittest
from base64 import b64encode

from unittest.mock import patch

from spresso.utils.base import get_file_content, update_existing_keys, \
    get_url, to_b64, from_b64, create_nonce, \
    create_random_characters, get_resource


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.scheme = "https"
        self.netloc = "example.com"
        self.path = "/"
        self.verify = True
        self.timestamp_file = "timestamp"
        self.caching_file = "cache"

    def test_create_nonce(self):
        length = 20
        nonce = create_nonce(length)
        self.assertEqual(len(nonce), length)

    def test_create_random_characters(self):
        length = 20
        chars = string.ascii_uppercase + string.digits
        random_chars = create_random_characters(length, chars=chars)

        self.assertEqual(len(random_chars), length)
        for c in random_chars:
            self.assertIn(c, chars)

    def test_get_file_content(self):
        mode = "w"
        rel_path = "test"
        self.assertRaises(ValueError, get_file_content, rel_path, mode)

        mode = "r"
        self.assertRaises(ValueError, get_file_content, None, mode)

        self.assertRaises(FileNotFoundError, get_file_content, rel_path, mode)

        actual_path = os.path.normpath(__file__)
        with open(actual_path, "r") as file:
            self.assertEqual(file.read(), get_file_content(__file__, mode))

        with open(actual_path, "r") as file:
            self.assertEqual(file.read(), get_file_content(actual_path, mode))

    def test_update_existing_keys(self):
        source = dict()
        target = dict(target_entry="test")

        update_existing_keys(source, target)
        self.assertEqual(len(target), 1)

        source.update(dict(test="test"))
        update_existing_keys(source, target)
        self.assertEqual(len(target), 1)

        source.update(dict(target_entry="changed entry"))
        update_existing_keys(source, target)
        self.assertEqual(len(target), 1)
        self.assertEqual(target["target_entry"], "changed entry")

    def test_get_url(self):
        scheme = "ftp"
        netloc = "example.com"

        self.assertEqual(get_url(scheme, netloc), "ftp://example.com")
        self.assertEqual(get_url(scheme, netloc, "/test"),
                         "ftp://example.com/test")

    def test_b64_encoding(self):
        data = "string"
        data_enc = to_b64(data)
        self.assertEqual(str, type(data_enc))

        data_bytes = data.encode('utf-8')
        data_bytes_enc = to_b64(data_bytes)
        self.assertEqual(str, type(data_bytes_enc))

        test = b64encode(data.encode('utf-8')).decode('utf-8')
        self.assertEqual(data_enc, test)
        self.assertEqual(data_bytes_enc, test)

    def test_b64_decoding(self):
        data = "string"
        data_b64_bytes = b64encode(data.encode('utf-8'))
        data_b64 = data_b64_bytes.decode('utf-8')

        test = from_b64(data_b64)
        test_bytes = from_b64(data_b64_bytes)
        self.assertEqual(str, type(test))
        self.assertEqual(str, type(test_bytes))
        self.assertEqual(test, data)
        self.assertEqual(test_bytes, data)

        test = from_b64(data_b64, return_bytes=True)
        test_bytes = from_b64(data_b64_bytes, return_bytes=True)
        self.assertEqual(bytes, type(test))
        self.assertEqual(bytes, type(test_bytes))
        self.assertEqual(test, data.encode('utf-8'))
        self.assertEqual(test_bytes, data.encode('utf-8'))

    @patch("spresso.utils.base.pkgutil")
    def test_get_resource(self, pkgutil_mock):
        pkgutil_mock.get_data.return_value = "test".encode('utf-8')

        self.assertEqual(get_resource("resource/", "path"), "test")
        pkgutil_mock.get_data.assert_called_once_with(
            "spresso",
            "resource/path"
        )
