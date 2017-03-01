import unittest
from unittest.mock import Mock, patch

from spresso.model.web.base import Response
from spresso.view.base import json_error_response, json_success_response, \
    View, JsonView, TemplateBase, TemplateView, Script


class JsonResponseTestCase(unittest.TestCase):
    def test_json_error_response(self):
        response = Mock()
        error = Mock()
        error.error = "test"
        error.explanation = "explanation"
        res = json_error_response(error, response, 500)

        response.add_header.assert_called_once_with(
            "Content-Type",
            "application/json"
        )
        self.assertEqual(res.status_code, 500)
        self.assertIn("test", res.data)
        self.assertIn("explanation", res.data)

    def test_json_success_response(self):
        response = Mock()
        data = "test"
        res = json_success_response(data, response)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, res.data)


class ViewTestCase(unittest.TestCase):
    def test_process(self):
        view = View()

        response = Mock()
        self.assertIsInstance(view.process(response), Response)

        response = Mock(spec=Response)
        self.assertEqual(view.process(response), response)


class TestJsonView(JsonView):
    def json(self):
        return "json"


@patch("spresso.view.base.json_success_response")
class JsonViewTestCase(unittest.TestCase):
    def test_make_response(self, json_response_mock):
        json_response_mock.return_value = "view"
        response = Mock()

        json_view = TestJsonView()

        res = json_view.make_response(response)
        self.assertEqual(res, "view")
        json_response_mock.assert_called_once_with("json", response)


class TestTemplateBase(TemplateBase):
    template_context = dict(key="value")

    def template(self):
        return "resource"


class TemplateTestCase(unittest.TestCase):
    @patch("spresso.view.base.get_resource")
    @patch("spresso.view.base.Template")
    def test_template_base(self, template_mock, get_resource_mock):
        settings = Mock()
        settings.resource_path = "path"

        template = Mock()

        template.render.return_value = "template"
        template_mock.return_value = template

        get_resource_mock.return_value = "content"

        test = TestTemplateBase(settings=settings)

        self.assertEqual(test.render(), "template")
        get_resource_mock.assert_called_once_with("path", "resource")
        template_mock.assert_called_once_with("content", autoescape=False)
        template.render.assert_called_once_with(key="value", settings=settings)

    @patch("spresso.view.base.TemplateBase.render")
    def test_template(self, base_mock):
        base_mock.return_value = "data"
        settings = Mock()
        test = TemplateView(settings=settings)

        response = Mock()
        res = test.make_response(response)

        base_mock.assert_called_once_with()
        self.assertEqual(response.data, "data")
        self.assertEqual(res, response)

    def test_script(self):
        settings = Mock()
        settings.js_template = "template"

        test = Script(settings=settings)
        self.assertEqual(test.template(), "template")
