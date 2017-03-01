import unittest
from unittest.mock import Mock, patch

from spresso.controller.grant.api.api import ApiInformationHandler
from spresso.controller.grant.api.settings import ApiInformationSettings


class ApiInformationGrantTestCase(unittest.TestCase):
    @patch("spresso.controller.grant.api.api.ApiView")
    def test_api_information_handler(self, view_mock):
        settings = Mock(spec=ApiInformationSettings)
        application = Mock()
        application.grant_types = "grants"
        handler = ApiInformationHandler(application, settings=settings)

        request = Mock()
        response = Mock()
        environ = Mock()

        view = Mock()
        view.process.return_value = "response"
        view_mock.return_value = view

        res = handler.process(request, response, environ)

        view_mock.assert_called_once_with(settings=settings)
        self.assertEqual(view.template_context, dict(grants="grants"))
        view.process.assert_called_once_with(response)
        self.assertEqual(res, "response")
