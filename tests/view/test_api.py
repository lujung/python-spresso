import unittest

from unittest.mock import Mock

from spresso.view.api.api import ApiView


class ProxyViewTestCase(unittest.TestCase):
    def test_json(self):
        settings = Mock()
        settings.api_template = "api"
        api_view = ApiView(settings=settings)

        self.assertEqual(api_view.template(), "api")
