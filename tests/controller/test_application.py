import json
import unittest
from unittest.mock import Mock

from spresso.controller.application import Application
from spresso.controller.grant.authentication.site_adapter.base import \
    AuthenticatingSiteAdapter
from spresso.controller.grant.base import ValidatingGrantHandler
from spresso.model.web.base import Response
from spresso.utils.error import SpressoInvalidError


class ApplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.response_mock = Mock(spec=Response)
        self.response_mock.body = ""
        response_class_mock = Mock(return_value=self.response_mock)

        self.application = Application(
            response_class=response_class_mock
        )

    def test_dispatch(self):
        environ = {"session": "data"}
        process_result = "info_class"

        request_mock = Mock(spec=Response)

        grant_handler_mock = Mock(spec=ValidatingGrantHandler)
        grant_handler_mock.process.return_value = process_result

        grant_factory_mock = Mock(return_value=grant_handler_mock)

        self.application.site_adapter = Mock(
            spec=AuthenticatingSiteAdapter
        )

        self.application.add_grant(grant_factory_mock)
        result = self.application.dispatch(request_mock, environ)

        grant_factory_mock.assert_called_with(
            request_mock,
            self.application,
        )
        grant_handler_mock.read_validate_params.assert_called_with(request_mock)
        grant_handler_mock.process.assert_called_with(
            request_mock,
            self.response_mock,
            environ
        )
        self.assertEqual(result, process_result)

    def test_dispatch_no_grant_type_found(self):
        error_body = {
            "error": "unsupported_grant",
            "error_description": "Grant not supported"
        }

        request_mock = Mock(spec=Response)

        result = self.application.dispatch(request_mock, {})

        self.response_mock.add_header.assert_called_with(
            "Content-Type", "application/json"
        )
        self.assertEqual(self.response_mock.status_code, 400)
        self.assertEqual(self.response_mock.body, json.dumps(error_body))
        self.assertEqual(result, self.response_mock)

    def test_dispatch_general_exception(self):
        request_mock = Mock(spec=Response)

        grant_handler_mock = Mock(spec=ValidatingGrantHandler)
        grant_handler_mock.process.side_effect = ValueError

        grant_factory_mock = Mock(return_value=grant_handler_mock)
        self.application.add_grant(grant_factory_mock)
        self.application.dispatch(request_mock, {})

        self.assertTrue(grant_handler_mock.handle_error.called)

    def test_dispatch_grant_error(self):
        request_mock = Mock(spec=Response)

        grant_handler_mock = Mock(spec=ValidatingGrantHandler)
        grant_handler_mock.process.side_effect = SpressoInvalidError("")

        grant_factory_mock = Mock(return_value=grant_handler_mock)
        self.application.add_grant(grant_factory_mock)
        self.application.dispatch(request_mock, {})

        self.assertTrue(grant_handler_mock.handle_error.called)
