import unittest

from unittest.mock import Mock

from spresso.view.authentication.forward import ProxyView


class ProxyViewTestCase(unittest.TestCase):
    def test_json(self):
        settings = Mock()
        settings.proxy_template = "proxy"
        proxy_view = ProxyView(settings=settings)

        self.assertEqual(proxy_view.template(), "proxy")
