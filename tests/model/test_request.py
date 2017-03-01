import unittest

from unittest.mock import patch, Mock

from spresso.model.request import GetRequest
from spresso.utils.error import SpressoInvalidError


class GetRequestTestCase(unittest.TestCase):
    @patch("spresso.model.request.requests")
    @patch("spresso.model.request.get_url")
    def test_request(self, get_url_mock, requests_mock):
        scheme = "scheme"
        netloc = "netloc"
        path = "path"
        verify = "verify"
        proxies = "proxies"

        get_url_mock.return_value = "url"

        get_request = GetRequest(scheme, netloc, path, verify, proxies)

        get_url_mock.assert_called_once_with(scheme, netloc, path)
        self.assertEqual(get_request.url, "url")
        self.assertEqual(get_request.verify, verify)
        self.assertEqual(get_request.proxies, proxies)

        requests_mock.get.side_effect = Exception
        self.assertRaises(SpressoInvalidError, get_request.request)
        requests_mock.get.side_effect = None

        res = Mock()
        res.status_code = 0
        requests_mock.get.return_value = res
        self.assertRaises(SpressoInvalidError, get_request.request)

        res.status_code = 200
        requests_mock.reset_mock()

        response = get_request.request()
        requests_mock.get.assert_called_once_with(
            url="url",
            verify=verify,
            proxies=proxies
        )
        self.assertEqual(response, res)
