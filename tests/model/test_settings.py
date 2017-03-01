import unittest

from unittest.mock import Mock

from spresso.model.base import JsonSchema
from spresso.model.settings import Entry, Endpoint, Schema, Domain, \
    ForwardDomain, CachingSetting, Container, SelectionContainer


class SettingsTestCase(unittest.TestCase):
    def test_entry(self):
        entry = Entry()
        self.assertIsNone(entry.name)
        self.assertEqual(str(entry), 'Entry({})')

    def test_endpoint(self):
        name = "name"
        path = 0
        methods = ""

        with self.assertRaises(ValueError):
            Endpoint(name, path, methods)
            path = ""
            Endpoint(name, path, methods)
            path = "/"
            Endpoint(name, path, methods)
            methods = ["TEST"]
            Endpoint(name, path, methods)

        path = "/"
        methods = []
        endpoint = Endpoint(name, path, methods)
        self.assertEqual(endpoint.name, name)
        self.assertEqual(endpoint.path, path)
        self.assertEqual(endpoint.methods, methods)

    def test_schema(self):
        name = "name"
        json = ""

        self.assertRaises(ValueError, Schema, name, json)
        json = Mock(spec=JsonSchema)

        schema = Schema(name, json)
        self.assertEqual(schema.name, name)
        self.assertEqual(schema.schema, json)

    def test_domain(self):
        domain = Domain("name", "test")
        self.assertEqual(domain.name, "name")
        self.assertEqual(domain.domain, "test")

    def test_forward_domain(self):
        name = ""
        domain = ""
        fwd_domain = ForwardDomain(name, domain)
        self.assertTrue(fwd_domain.padding)
        fwd_domain = ForwardDomain(name, domain, padding=False)
        self.assertFalse(fwd_domain.padding)

    def test_caching_setting(self):
        name = "name"
        in_memory = ""
        lifetime = ""

        with self.assertRaises(ValueError):
            CachingSetting(name, in_memory, lifetime)
            in_memory = True
            CachingSetting(name, in_memory, lifetime)

        in_memory = True
        lifetime = 1
        setting = CachingSetting(name, in_memory, lifetime)
        self.assertEqual(setting.name, name)
        self.assertEqual(setting.in_memory, in_memory)
        self.assertEqual(setting.lifetime, lifetime)


class ContainerTestCase(unittest.TestCase):
    def test_init(self):
        entry = Entry()
        entry.name = "name"
        container = Container(entry)
        self.assertIsNone(container.name)
        self.assertEqual(container._dictionary.get("name"), entry)

    def test_update(self):
        container = Container()
        self.assertRaises(ValueError, container.update, "")

        entry = Entry()
        entry.name = "name"
        container.update(entry)
        self.assertIn(entry, container._dictionary.values())

    def test_get(self):
        container = Container()
        container._dictionary.update(dict(key="value"))
        self.assertEqual(container.get("key"), "value")

    def test_all(self):
        container = Container()
        self.assertEqual(container.all(), dict())


class SelectionContainerTestCase(unittest.TestCase):
    def test_init(self):
        select = SelectionContainer("random", default="test")
        self.assertEqual(select._strategy, "random")
        self.assertEqual(select._dictionary["default"], "test")

    def test_select_random(self):
        select = SelectionContainer("random")
        values = ["test", "test2", "test3", "test4", "test5"]
        for value in values:
            select._dictionary.update({value: value})

        self.assertIn(select.select(), values)

    def test_select(self):
        select = SelectionContainer("select", default="default")
        values = ["test", "test2", "test3", "test4", "test5"]
        for value in values:
            select._dictionary.update({value: value})

        self.assertEqual(select.select(), "default")
        self.assertEqual(select.select("test3"), "test3")

    def test_update_default(self):
        select = SelectionContainer("select", default="default")
        select.update_default("test")
        self.assertEqual(select._dictionary["default"], "test")

    def test_set_strategy(self):
        select = SelectionContainer("select")
        self.assertRaises(ValueError, select.set_strategy, "")
        select.set_strategy("random")
        self.assertEqual(select._strategy, "random")
