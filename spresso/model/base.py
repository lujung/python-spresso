import json
import re
from urllib.parse import urlparse

from jsonschema import validate

from spresso.utils.base import get_resource, get_url


class Composition(dict):
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def to_json(self):
        return json.dumps(self, sort_keys=True)

    def from_json(self, data):
        data_json = json.loads(data)

        for key, value in data_json.items():
            self[key] = value


class SettingsMixin(object):
    def __init__(self, settings):
        super(SettingsMixin, self).__init__()
        self.settings = settings


class JsonSchema(object):
    resource_path = "resources/"
    file_path = ""

    def validate(self, data_dict):
        schema = json.loads(self.get_schema())
        validate(data_dict, schema)

    def get_schema(self):
        return get_resource(self.resource_path, self.file_path)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, vars(self))


class Origin(SettingsMixin):
    def __init__(self, request_header, **kwargs):
        super(Origin, self).__init__(**kwargs)
        self.request_header = request_header

    @property
    def expected(self):
        return get_url(self.settings.scheme, self.settings.domain)

    @property
    def valid(self):
        return urlparse(self.expected) == urlparse(self.request_header)


class User(object):
    def __init__(self, email, regexp=r"^[^#&]+@([a-zA-Z0-9-.]+)$"):
        self.email = email
        self.regexp = regexp

    @property
    def netloc(self):
        if self.is_valid:
            return re.split('@', self.email)[1]
        return None

    @property
    def is_valid(self):
        return self.email and self.basic_check()

    def basic_check(self):
        return re.search(self.regexp, self.email) is not None
