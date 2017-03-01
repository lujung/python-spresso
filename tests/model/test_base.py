import json
import unittest
from json import JSONDecodeError
from unittest.mock import patch, Mock

from spresso.model.base import Composition, User, JsonSchema, Origin
from spresso.utils.base import get_url


class CompositionTestCase(unittest.TestCase):
    def test_init(self):
        c = Composition()
        self.assertEqual(c, {})

    def test_from_json(self):
        test = dict(key="value")
        test_json = json.dumps(test)
        c = Composition()
        c.from_json(test_json)
        self.assertEqual(c, test)

        invalid_json = "json fail"
        self.assertRaises(JSONDecodeError, c.from_json, invalid_json)

    def test_to_json(self):
        c = Composition(key="value")
        test = dict(key="value")
        test_json = json.dumps(test)

        self.assertEqual(c.to_json(), test_json)

    def test_set_get(self):
        c = Composition(key="value")
        self.assertEqual(c.key, "value")

        c.key = "test"
        self.assertEqual(c.key, "test")


class JsonSchemaTestCase(unittest.TestCase):
    @patch("spresso.model.base.validate")
    @patch("spresso.model.base.get_resource")
    @patch("spresso.model.base.json")
    def test_validate(self, json_mock, get_resource_mock, validate_mock):
        json_schema = JsonSchema()
        data = ""
        json_mock.loads.return_value = "schema"
        get_resource_mock.return_value = "resource"
        json_schema.validate(data)

        json_mock.loads.assert_called_once_with("resource")
        validate_mock.assert_called_once_with(data, "schema")

    @patch("spresso.model.base.get_resource")
    def test_get_schema(self, resource_mock):
        json_schema = JsonSchema()
        resource_mock.return_value = "schema"
        schema = json_schema.get_schema()
        resource_mock.assert_called_once_with("resources/", "")
        self.assertEqual(schema, "schema")

    def test_str(self):
        json_schema = JsonSchema()
        self.assertEqual(str(json_schema), 'JsonSchema({})')


class OriginTestCase(unittest.TestCase):
    @patch("spresso.model.base.get_url")
    @patch("spresso.model.base.urlparse")
    def test_origin(self, urlparse_mock, get_url_mock):
        header = "header"
        settings = Mock()
        settings.scheme = "scheme"
        settings.domain = "domain"
        origin = Origin(header, settings=settings)

        get_url_mock.return_value = "url"
        urlparse_mock.return_value = "urlparse"

        self.assertTrue(origin.valid)
        get_url_mock.assert_called_once_with("scheme", "domain")
        self.assertEqual(urlparse_mock.call_count, 2)

    def test_functional(self):
        scheme = "http"
        netloc = "example.com"
        url = get_url(scheme, netloc)

        settings = Mock()
        settings.scheme = scheme
        settings.domain = netloc
        origin = Origin(url, settings=settings)

        self.assertEqual(origin.expected, scheme + "://" + netloc)
        self.assertTrue(origin.valid)

        scheme = "https"
        mismatching_url = get_url(scheme, netloc)
        origin = Origin(mismatching_url, settings=settings)
        self.assertFalse(origin.valid)


class UserTestCase(unittest.TestCase):
    def test_netloc(self):
        user = User(None)
        self.assertIsNone(user.netloc)

        user.email = "test@test"
        self.assertEqual(user.netloc, "test")

    def test_valid(self):
        user = User(None)
        self.assertFalse(user.is_valid)

        user.email = "test@test"
        self.assertTrue(user.is_valid)

    def test_basic_check(self):
        invalid_email = "test#d@test"
        user = User(invalid_email)
        self.assertFalse(user.basic_check())

        valid_email = "test@test"
        user.email = valid_email
        self.assertTrue(user.basic_check())
