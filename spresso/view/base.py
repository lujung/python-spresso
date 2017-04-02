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
            returned a default instance of type `response_class` is returned.

            Args:
                response: The response.

            Returns:
                The verified response of type `response_class`.
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
                The response parameter.
        """
        return response


class JsonView(View):
    """Abstract JSON view class."""

    def make_response(self, response):
        """Wrapper around :func:`json_success_response`. Retrieves the JSON
            data by calling :func:`json`.
            
            Args:
                response (:class:`spresso.model.web.base.Response`): The 
                    response.

            Returns:
                The response returned by :func:`json_success_response`.
        """
        return json_success_response(self.json(), response)

    def json(self):
        """Provides the actual JSON content. Has to be implemented by inheriting
            classes"""
        raise NotImplementedError


class TemplateBase(SettingsMixin):
    """Abstract template view class. Uses `Jinja2
        <http://jinja.pocoo.org/docs/2.9/>`_ for template rendering, enabling 
            the use of Jinja2 functionality in templates."""
    template_context = dict()

    def render(self):
        """The configuration object is mixed in. A template is chosen, loaded 
            and rendered.

            Returns:
                The rendered template.
        """
        self.template_context.update(dict(settings=self.settings))
        template_file = get_resource(
            self.settings.resource_path,
            self.template()
        )
        template = Template(template_file, autoescape=False)
        return template.render(**self.template_context)

    def template(self):
        """Abstract template file definition. Has to be implemented by 
            inheriting classes.

            Returns:
                The template file path.
        """
        raise NotImplementedError


class TemplateView(View, TemplateBase):
    """Abstract template view class that inserts the template in a HTTP
        response."""

    def make_response(self, response):
        """Wrapper around :func:`render`. Adds the rendered template to the 
            response object.

            Args:
                response (:class:`spresso.model.web.base.Response`): The 
                    response.

            Returns:
                The response containing the template.
        """
        response.data = super(TemplateView, self).render()
        return response


class Script(TemplateBase):
    """Template view class that is used to render a JavaScript used in SPRESSO.
    """

    def template(self):
        """Return the JS template file from the settings.

            Returns:
                The template file path.
        """
        return self.settings.js_template
