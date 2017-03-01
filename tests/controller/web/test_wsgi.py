import unittest
from unittest.mock import Mock, patch, MagicMock

from spresso.controller.application import Application
from spresso.controller.web.wsgi import WsgiApplication, PathDispatcher
from spresso.model.settings import Endpoint
from spresso.model.web.base import Request, Response


class WSGIApplicationTestCase(unittest.TestCase):
    @patch("spresso.controller.web.wsgi.WsgiRequest")
    def test_call(self, request_class_mock):
        data = "body"
        headers = {"request_header": "value"}
        path = "/authorize"
        request_method = "GET"
        status_code = 200
        http_code = "200 OK"
        http_code_not_found = "404 NOT FOUND"

        environment = {"PATH_INFO": path, "REQUEST_METHOD": request_method}

        request_mock = Mock(spec=Request)
        request_class_mock.return_value = request_mock

        response_mock = Mock(spec=Response)
        response_mock.data = data
        response_mock.headers = headers
        response_mock.status_code = status_code

        application_mock = MagicMock(spec=Application)
        endpoints = Endpoint("authorize", path, [request_method])

        grant_mock = Mock()
        grant_mock.settings.endpoints.all.return_value = dict(test=endpoints)
        application_mock.grant_types = [grant_mock]

        application_mock.dispatch.return_value = response_mock

        start_response_mock = Mock()

        wsgi = WsgiApplication(application_mock)
        result = wsgi(environment, start_response_mock)

        request_class_mock.assert_called_once_with(environment)
        application_mock.dispatch.assert_called_with(request_mock, environment)
        start_response_mock.assert_called_with(http_code, list(headers.items()))
        self.assertEqual(result, [data.encode('utf-8')])

        # Call some url
        environment.update(dict(PATH_INFO="/"))

        wsgi(environment, start_response_mock)
        start_response_mock.assert_called_with(
            http_code_not_found,
            [('Content-Type', 'text/plain')]
        )


class PathDispatcherTestCase(unittest.TestCase):
    @patch("spresso.controller.web.wsgi.WsgiRequest")
    def test_call(self, request_class_mock):
        data = "body"
        headers = {"request_header": "value"}
        path = "/test"
        request_method = "GET"
        status_code = 200
        http_code = "200 OK"

        environment = {"PATH_INFO": path, "REQUEST_METHOD": request_method}

        request_mock = Mock(spec=Request)
        request_class_mock.return_value = request_mock

        response_mock = Mock(spec=Response)
        response_mock.data = data
        response_mock.headers = headers
        response_mock.status_code = status_code

        application_mock = MagicMock(spec=Application)

        endpoints = Endpoint("test", path, [request_method])

        grant_mock = Mock()
        grant_mock.settings.endpoints.all.return_value = dict(test=endpoints)
        application_mock.grant_types = [grant_mock]
        application_mock.dispatch.return_value = response_mock

        default_application_mock = MagicMock(spec=Application)

        endpoints = Endpoint("index", "/", ["GET", "POST"])
        grant_mock = Mock()
        grant_mock.settings.endpoints.all.return_value = dict(test=endpoints)
        default_application_mock.grant_types = [grant_mock]

        default_application_mock.dispatch.return_value = response_mock

        start_response_mock = Mock()

        wsgi = WsgiApplication(application=application_mock)
        default_wsgi = WsgiApplication(application=default_application_mock)

        path_dispatcher = PathDispatcher(default_app=default_wsgi, app=wsgi)

        # Call /test
        result = path_dispatcher(environment, start_response_mock)

        request_class_mock.assert_called_once_with(environment)
        application_mock.dispatch.assert_called_with(request_mock, environment)
        start_response_mock.assert_called_with(http_code, list(headers.items()))
        self.assertEqual(result, [data.encode('utf-8')])

        # Call url that is not in provider_mock
        environment.update(dict(PATH_INFO="/"))
        result = path_dispatcher(environment, start_response_mock)

        default_application_mock.dispatch.assert_called_with(
            request_mock,
            environment
        )
        start_response_mock.assert_called_with(http_code, list(headers.items()))
        self.assertEqual(result, [data.encode('utf-8')])
