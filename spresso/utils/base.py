import os
import pkgutil
import random
import string
from base64 import b64encode, b64decode
from urllib.parse import ParseResult, urlunparse


def create_nonce(length):
    """
    Generates random_choice bit string.
    UNIX-like system will query /dev/urandom, Windows will use CryptGenRandom()
    :param length: int
    :return: byte
    """
    return os.urandom(length)


def create_random_characters(length,
                             chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def get_file_content(path, mode):
    if mode not in ["r", "rb"]:
        raise ValueError("mode must be 'r' or 'rb'")

    if path is None:
        raise ValueError("rel_path must be path to file")

    if not os.path.isabs(path):
        path = os.path.abspath(path)

    if not os.path.isfile(path):
        raise FileNotFoundError(
            "File could not be found at {0}".format(path))

    with open(path, mode) as current_file:
        return current_file.read()


def update_existing_keys(source, target):
    for key, value in source.items():
        if key in target:
            target.update({key: value})


def get_url(scheme, netloc, path="", params="", query="", fragment=""):
    url = ParseResult(scheme, netloc, path, params, query, fragment)
    return urlunparse(url)


def to_b64(data):
    if isinstance(data, str):
        data = data.encode('utf-8')

    data_b64 = b64encode(data)
    return data_b64.decode('utf-8')


def from_b64(data_b64, return_bytes=False):
    if isinstance(data_b64, str):
        data_b64 = data_b64.encode('utf-8')

    data = b64decode(data_b64)
    if return_bytes:
        return data

    return data.decode('utf-8')


def get_resource(resource_path, path):
    template_js = pkgutil.get_data(
        'spresso',
        '{}{}'.format(resource_path, path)
    )
    return template_js.decode('utf-8')
