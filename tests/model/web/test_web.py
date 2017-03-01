import unittest
from unittest.mock import Mock

from spresso.model.web.base import Response
from spresso.model.web.wsgi import WsgiRequest


class WsgiRequestTestCase(unittest.TestCase):
    def test_initialization_no_post_data(self):
        request_method = "TEST"
        query_string = "foo=bar&baz=buz"

        environment = {"REQUEST_METHOD": request_method,
                       "QUERY_STRING": query_string,
                       "PATH_INFO": "/"}

        request = WsgiRequest(environment)

        self.assertEqual(request.method, request_method)
        self.assertEqual(request.query_params, {"foo": "bar", "baz": "buz"})
        self.assertEqual(request.query_string, query_string)
        self.assertEqual(request.post_params, {})

    def test_initialization_with_post_data(self):
        content_length = "42"
        request_method = "POST"
        query_string = ""
        content = "foo=bar&baz=buz".encode('utf-8')

        wsgi_input_mock = Mock(spec=["read"])
        wsgi_input_mock.read.return_value = content

        environment = {"CONTENT_LENGTH": content_length,
                       "CONTENT_TYPE": "application/x-www-form-urlencoded",
                       "REQUEST_METHOD": request_method,
                       "QUERY_STRING": query_string,
                       "PATH_INFO": "/",
                       "wsgi.input": wsgi_input_mock}

        request = WsgiRequest(environment)

        wsgi_input_mock.read.assert_called_with(int(content_length))
        self.assertEqual(request.method, request_method)
        self.assertEqual(request.query_params, {})
        self.assertEqual(request.query_string, query_string)
        self.assertEqual(request.post_params, {"foo": "bar", "baz": "buz"})

    def test_get_param(self):
        request_method = "TEST"
        query_string = "foo=bar&baz=buz"

        environment = {"REQUEST_METHOD": request_method,
                       "QUERY_STRING": query_string,
                       "PATH_INFO": "/a-url"}

        request = WsgiRequest(environment)

        result = request.get_param("foo")

        self.assertEqual(result, "bar")

        result_default = request.get_param("na")

        self.assertEqual(result_default, None)

    def test_post_param(self):
        content_length = "42"
        request_method = "POST"
        query_string = ""
        content = "foo=bar&baz=buz".encode('utf-8')

        wsgi_input_mock = Mock(spec=["read"])
        wsgi_input_mock.read.return_value = content

        environment = {"CONTENT_LENGTH": content_length,
                       "CONTENT_TYPE": "application/x-www-form-urlencoded",
                       "REQUEST_METHOD": request_method,
                       "QUERY_STRING": query_string,
                       "PATH_INFO": "/",
                       "wsgi.input": wsgi_input_mock}

        request = WsgiRequest(environment)

        result = request.post_param("foo")

        self.assertEqual(result, "bar")

        result_default = request.post_param("na")

        self.assertEqual(result_default, None)

        wsgi_input_mock.read.assert_called_with(int(content_length))

    def test_header(self):
        environment = {"REQUEST_METHOD": "GET",
                       "QUERY_STRING": "",
                       "PATH_INFO": "/",
                       "HTTP_AUTHORIZATION": "Basic abcd"}

        request = WsgiRequest(env=environment)

        self.assertEqual(request.header("authorization"), "Basic abcd")
        self.assertIsNone(request.header("unknown"))
        self.assertEqual(request.header("unknown", default=0), 0)

    def test_cookie(self):
        environment = {
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "",
            "PATH_INFO": "/",
            "HTTP_COOKIE": "key=value"
        }

        request = WsgiRequest(env=environment)

        self.assertIn('key', request.cookies)
        self.assertEqual(request.get_cookie('key'), 'value')
        self.assertEqual(request.get_cookie('test'), None)

        del environment["HTTP_COOKIE"]
        request = WsgiRequest(env=environment)

        self.assertEqual(request.cookies, {})


class ResponseTestCase(unittest.TestCase):
    def test_header(self):
        response = Response()
        response.add_header('key', 'value')

        self.assertIn('key', response.headers)

    def test_cookie(self):
        response = Response()
        response.set_cookie('key', 'value')

        self.assertIn("Set-Cookie", response.headers)
        self.assertIn("key=value", response.headers["Set-Cookie"])
