import json

from jinja2 import Template

from spresso.model.base import SettingsMixin
from spresso.model.web.base import Response
from spresso.utils.base import get_resource


def json_error_response(error, response, status_code=400):
    """Method for returning a JSON error response, based on a 
        :class:`spresso.utils.error.SpressoBaseError`.

        Args:
            error (:class:`spresso.utils.error.SpressoBaseError`): The error.
            response (:class:`spresso.model.web.base.Response`): The response.
            status_code (int): The HTTP status code.

        Returns:
            :class:`spresso.model.web.base.Response`: The response containing
             the error.
    """
    msg = {"error": error.error, "error_description": error.explanation}

    if error.uri:
        msg.update(dict(uri="{0}".format(error.uri)))

    response.status_code = status_code
    response.add_header("Content-Type", "application/json")
    response.data = json.dumps(msg)

    return response


def json_success_response(data, response):
    """Method for returning a JSON success response, based on response data.

        Args:
            data (str): The response data.
            response (:class:`spresso.model.web.base.Response`): The response.

        Returns:
            :class:`spresso.model.web.base.Response`: The response containing 
            the data.
    """
    response.data = data
    response.status_code = 200

    response.add_header("Content-Type", "application/json")
    response.add_header("Cache-Control", "no-store")
    response.add_header("Pragma", "no-cache")

    return response


class View(object):
    """Basic view class.

        Args:
            response_class (optional): The response class, defaults to 
            :class:`spresso.model.web.base.Response`.
    """
    def __init__(self, response_class=Response, **kwargs):
        super(View, self).__init__(**kwargs)
        self.response_class = response_class

    def process(self, response):
        """Wrapper around :func:`make_response`. If no valid response is
         returned a default instance is returned.

            Args:
                response (:class:`spresso.model.web.base.Response`): The 
                response.

            Returns:
                :obj:: The verified response of type `response_class`.
        """
        response = self.make_response(response)

        if isinstance(response, self.response_class):
            return response

        return self.response_class()

    def make_response(self, response):
        """Basic Interface method. Can be extended by inheriting classes.

            Args:
                response (:class:`spresso.model.web.base.Response`): The 
                response.

            Returns:
                :obj:: The response parameter.
        """
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
