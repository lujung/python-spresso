import requests

from spresso.utils.base import get_url
from spresso.utils.error import SpressoInvalidError


class GetRequest(object):
    """
        Class to resolve GET requests.
    """

    def __init__(self, scheme, netloc, path, verify, proxies):
        super(GetRequest, self).__init__()
        self.url = get_url(scheme, netloc, path)
        self.verify = verify
        self.proxies = proxies

    def request(self):
        try:
            res = requests.get(
                url=self.url,
                verify=self.verify,
                proxies=self.proxies
            )
        except Exception as e:
            raise SpressoInvalidError(
                error="connection_error",
                message="{0}".format(e),
                uri=self.url
            )
        if res.status_code != 200:
            raise SpressoInvalidError(
                error="invalid_status",
                message="Received HTTP status code {0}".format(res.status_code),
                uri=self.url
            )
        return res
