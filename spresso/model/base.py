import json
import re
from urllib.parse import urlparse

from jsonschema import validate

from spresso.utils.base import get_resource, get_url


class Composition(dict):
    """Extension to :py:class:`dict`, defining the base for all SPRESSO specific
        objects used by the system. Enables object-like access to dictionary 
        instances, as well as import from JSON and export to JSON.
    """
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def to_json(self):
        """Serialize an object values to JSON. The keys are sorted, as some 
            operations in the SPRESSO flow depend on a unique representation.
            json.dumps is used, because data is transmitted over the web.
            
            Returns:
                str: The serialized object.
        """
        return json.dumps(self, sort_keys=True)

    def from_json(self, data):
        """Unserialize an object from a string representation.
        
            Args:
                str: The serialized object.
        """
        data_json = json.loads(data)

        for key, value in data_json.items():
            self[key] = value


class SettingsMixin(object):
    """Mixin class for assigning a configuration object."""
    def __init__(self, settings):
        super(SettingsMixin, self).__init__()
        self.settings = settings


class JsonSchema(object):
    """Class to provide a schema validator."""
    resource_path = "resources/"
    file_path = ""

    def validate(self, data_dict):
        """Retrieve the schema and validate the obtained data.
            
            Args:
                dict: The data dictionary.
        """
        schema = json.loads(self.get_schema())
        validate(data_dict, schema)

    def get_schema(self):
        """Load a JSON schema from the resource folder.
            
            Returns:
                str: The JSON schema.
        """
        return get_resource(self.resource_path, self.file_path)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, vars(self))


class Origin(SettingsMixin):
    """Class for validating the origin header of a HTTP Request."""
    def __init__(self, request_header, **kwargs):
        super(Origin, self).__init__(**kwargs)
        self.request_header = request_header

    @property
    def expected(self):
        """Retrieve the valid header.
            
            Returns:
                str: The origin header.
        """
        return get_url(self.settings.scheme, self.settings.domain)

    @property
    def valid(self):
        """Compare the correct and the obtained header using 
            :func:`urllib.parse.urlparse`.
            
                Returns:
                    bool: Validity of the obtained origin header.
            """
        return urlparse(self.expected) == urlparse(self.request_header)


class User(object):
    """Basic user model."""
    def __init__(self, email, regexp=r"^[^#&]+@([a-zA-Z0-9-.]+)$"):
        self.email = email
        self.regexp = regexp

    @property
    def netloc(self):
        """Check if the email is valid and get the domain part.
        
            Returns:
                The domain of the email address or None.
        """
        if self.is_valid:
            return re.split('@', self.email)[1]
        return None

    @property
    def is_valid(self):
        """Test if the email is valid.
        
            Returns:
                bool: Validity of the email address.
        """
        return self.email and self.basic_check()

    def basic_check(self):
        """Match the email address against a regular expression and therefore
            check its validity.
            
            Returns:
                bool: Statement if the regex matched against the email address.
        """
        return re.search(self.regexp, self.email) is not None
