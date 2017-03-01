import json

from jinja2 import Template

from spresso.model.base import SettingsMixin
from spresso.model.web.base import Response
from spresso.utils.base import get_resource


def json_error_response(error, response, status_code=400):
    msg = {"error": error.error, "error_description": error.explanation}

    if error.uri:
        msg.update(dict(uri="{0}".format(error.uri)))

    response.status_code = status_code
    response.add_header("Content-Type", "application/json")
    response.data = json.dumps(msg)

    return response


def json_success_response(data, response):
    response.data = data
    response.status_code = 200

    response.add_header("Content-Type", "application/json")
    response.add_header("Cache-Control", "no-store")
    response.add_header("Pragma", "no-cache")

    return response


class View(object):
    def __init__(self, response_class=Response, **kwargs):
        super(View, self).__init__(**kwargs)
        self.response_class = response_class

    def process(self, response):
        response = self.make_response(response)

        if isinstance(response, self.response_class):
            return response

        return self.response_class()

    def make_response(self, response):
        return response


class JsonView(View):
    def make_response(self, response):
        return json_success_response(self.json(), response)

    def json(self):
        raise NotImplementedError


class TemplateBase(SettingsMixin):
    template_context = dict()

    def render(self):
        self.template_context.update(dict(settings=self.settings))
        template_file = get_resource(
            self.settings.resource_path,
            self.template()
        )
        template = Template(template_file, autoescape=False)
        return template.render(**self.template_context)

    def template(self):
        raise NotImplementedError


class TemplateView(View, TemplateBase):
    def make_response(self, response):
        response.data = super(TemplateView, self).render()
        return response


class Script(TemplateBase):
    def template(self):
        return self.settings.js_template
