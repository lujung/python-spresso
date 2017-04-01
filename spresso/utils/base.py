import os
import pkgutil
import random
import string
from base64 import b64encode, b64decode
from urllib.parse import ParseResult, urlunparse


def create_nonce(length):
    """Generates random bytes of specified length. UNIX-like system will query 
        /dev/urandom, Windows will use CryptGenRandom()

        Args:
            length (int): The length of the random sequence.

        Returns:
            bytes: The random sequence.
    """
    return os.urandom(length)


def create_random_characters(length,
                             chars=string.ascii_uppercase + string.digits):
    """Generates a random string of a specified length. Per default the charset
        consists of uppercase ASCII letters and digits.

        Args:
            length (int): The length of the random string sequence.
            chars (str): The charset from which to choose.

        Returns:
            str: The random string sequence.
    """
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def get_file_content(path, mode):
    """Wrapper around :py:func:`open`.

        Args:
            path (str): The path to the file.
            mode (str): The mode in which the file should be opened.

        Raises:
            ValueError: The path or mode is invalid.
            FileNotFoundError: The file could not found at the given path.

        Returns:
            str: The file contents.
    """
    if mode not in ["r", "rb"]:
        raise ValueError("mode must be 'r' or 'rb'")

    if path is None:
        raise ValueError("rel_path must be path to file")

    if not os.path.isabs(path):
        path = os.path.abspath(path)

    if not os.path.isfile(path):
        raise FileNotFoundError(
            "File could not be found at {0}".format(path)
        )

    with open(path, mode) as current_file:
        return current_file.read()


def update_existing_keys(source, target):
    """Wrapper around :py:func:`dict.update`.
        This function only updates the existing keys in the dictionary.

        Args:
            source (dict): The source dictionary.
            target (dict): The target dictionary.
    """
    for key, value in source.items():
        if key in target:
            target.update({key: value})


def get_url(scheme, netloc, path="", params="", query="", fragment=""):
    """Wrapper around :class:`urllib.parse.ParseResult` and  
        :func:`urllib.parse.urlunparse` to retrieve an URL.

        Args:
            scheme (str): The URL scheme.
            netloc (str): The URL domain.
            path (str): The URL path.
            params (str): The URL parameters.
            query (str): The URL query arguments.
            fragment (str): The URL fragment.
        
        Returns:
            str: The URL.
    """
    url = ParseResult(scheme, netloc, path, params, query, fragment)
    return urlunparse(url)


def to_b64(data):
    """Wrapper around :py:func:`base64.b64encode` to encode data using
        Base64.

        Args:
            data (str, :obj:`bytes`): The data.

        Returns:
            str: The Base64-encoded data.
    """
    if isinstance(data, str):
        data = data.encode('utf-8')

    data_b64 = b64encode(data)
    return data_b64.decode('utf-8')


def from_b64(data_b64, return_bytes=False):
    """Wrapper around :py:func:`base64.b64decode` to decode data using
        Base64.

        Args:
            data_b64 (str, :obj:`bytes`): The Base64-encoded data.
            return_bytes (bool): Flag to indicate if bytes or string should be 
                returned.

        Returns:
            str, :obj:`bytes`: The decoded data.
    """
    if isinstance(data_b64, str):
        data_b64 = data_b64.encode('utf-8')

    data = b64decode(data_b64)
    if return_bytes:
        return data

    return data.decode('utf-8')


def get_resource(resource_path, path):
    """Method to retrieve resource files from the package installation
        directory.

        Args:
            resource_path (str): The path where resources are stored.
            path (bool): The relative path to the resource.

        Returns:
            str: The file content of the resource.
    """
    resource = pkgutil.get_data(
        'spresso',
        '{}{}'.format(resource_path, path)
    )
    return resource.decode('utf-8')
