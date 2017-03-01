import unittest
from unittest.mock import Mock, patch

from spresso.controller.grant.authentication.forward import ProxyHandler
from spresso.controller.grant.authentication.config.forward import \
    Forward


class ForwardAuthenticationGrantTestCase(unittest.TestCase):
    @patch("spresso.controller.grant.authentication.forward.Script")
    @patch("spresso.controller.grant.authentication.forward.ProxyView")
    def test_proxy_handler(self, proxy_mock, script_mock):
        settings = Mock(spec=Forward)

        script = Mock()
        script.render.return_value = "script"
        script_mock.return_value = script

        view = Mock()
        proxy_mock.return_value = view

        handler = ProxyHandler(settings=settings)

        request = Mock()
        response = Mock()
        environ = Mock()

        # Test process
        handler.process(request, response, environ)

        script_mock.assert_called_once_with(settings=settings)
        proxy_mock.assert_called_once_with(settings=settings)
        self.assertEqual(script.render.call_count, 1)
        self.assertEqual(view.template_context, dict(script="script"))
        view.process.assert_called_once_with(response)
