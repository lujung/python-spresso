import random
from functools import partialmethod

from spresso.model.base import JsonSchema


class Entry(object):
    name = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, vars(self))


class Endpoint(Entry):
    _methods = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS"]

    def __init__(self, name, path, methods):
        self.name = name

        if not isinstance(path, str):
            raise ValueError("'path' must be a string value")
        if not path.startswith("/"):
            raise ValueError("'path' must start with '/'")
        self.path = path

        if not isinstance(methods, list):
            raise ValueError("'_methods' must be of type '{}'".format(list))
        for method in methods:
            if method not in self._methods:
                raise ValueError(
                    "HTTP method '{}' is not supported,"
                    " available methods are {}".format(method, self._methods)
                )
        self.methods = methods


class Schema(Entry):
    def __init__(self, name, schema):
        self.name = name
        if not isinstance(schema, JsonSchema):
            raise ValueError("'schema' must be an instance of {}".format(
                JsonSchema.__name__
            ))
        self.schema = schema


class Domain(Entry):
    def __init__(self, name, domain):
        self.name = name
        self.domain = domain


class ForwardDomain(Domain):
    def __init__(self, *args, padding=True):
        super(ForwardDomain, self).__init__(*args)
        # Security config
        # Side channel attack prevention
        self.padding = padding


class CachingSetting(Entry):
    def __init__(self, name, in_memory, lifetime):
        self.name = name

        if not isinstance(in_memory, bool):
            raise ValueError("'in_memory' must be a boolean value")
        self.in_memory = in_memory

        if not isinstance(lifetime, int):
            raise ValueError("'lifetime' must be an integer value")
        self.lifetime = lifetime


class Container(Entry):
    def __init__(self, *args, name=None):
        if name:
            self.name = name
        self._dictionary = dict()
        for entry in args:
            self.update(entry)

    def update(self, entry):
        if not isinstance(entry, Entry):
            raise ValueError(
                "Entry must inherit from '{}'".format(Entry.__name__)
            )
        self._dictionary.update({entry.name: entry})

    def get(self, name):
        return self._dictionary.get(name)

    def all(self):
        return self._dictionary


class SelectionContainer(Container):
    default_id = "default"
    _strategies = ["random", "select"]
    _strategy = None

    def __init__(self, strategy, *args, default=None, **kwargs):
        super(SelectionContainer, self).__init__(*args, **kwargs)
        self.set_strategy(strategy)
        if default:
            self.update_default(default)

    def select(self, name=None):
        if self._strategy == "select":
            select = self._dictionary.get(name)
            if not select:
                return self._dictionary.get(self.default_id)
            return select

        if self._strategy == "random" and len(self._dictionary) > 0:
            return random.choice(list(self._dictionary.values()))

        return None

    def update_default(self, value):
        self._dictionary.update({self.default_id: value})

    def set_strategy(self, strategy):
        if strategy not in self._strategies:
            raise ValueError("Strategy was not found, available inputs are {}"
                             .format(self._strategies))
        self._strategy = strategy

    set_random = partialmethod(set_strategy, "random")
    set_select_or_default = partialmethod(set_strategy, "select")
