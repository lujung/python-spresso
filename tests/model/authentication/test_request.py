import unittest

from unittest.mock import Mock, patch

from spresso.model.authentication.request import IdpInfoRequest


class IdpInfoRequestTestCase(unittest.TestCase):
    @patch("spresso.model.authentication.request.GetRequest")
    def test_get_content(self, request_mock):
        netloc = "netloc"
        settings = Mock()
        select = Mock()
        endpoint = Mock()
        endpoint.path = "path"
        select.get.return_value = endpoint
        settings.endpoints_ext.select.return_value = select
        settings.scheme_well_known_info = "scheme"
        settings.verify = "verify"
        settings.proxies = "proxies"
        request = Mock()
        request_mock.return_value = request
        idp_info_request = IdpInfoRequest(netloc, settings=settings)

        settings.endpoints_ext.select.assert_called_once_with("netloc")
        select.get.assert_called_once_with("info")
        request_mock.assert_called_once_with("scheme", "netloc", "path",
                                             "verify", "proxies")

        cache = Mock()
        cache.get.return_value = "cache"
        settings.cache = cache
        res = idp_info_request.get_content()
        self.assertEqual(res, "cache")

        cache.get.return_value = None

        response = Mock()
        response.text = "response"
        request.request.return_value = response
        settings.caching_settings.select.return_value = "config"

        cache.reset_mock()
        request.reset_mock()
        settings.reset_mock()
        res = idp_info_request.get_content()
        cache.get.assert_called_once_with("netloc")
        self.assertEqual(request.request.call_count, 1)
        settings.caching_settings.select.assert_called_once_with("netloc")
        cache.set.assert_called_once_with("netloc", "config", "response")

        self.assertEqual(res, "response")
