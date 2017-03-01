import json

from spresso.controller.grant.base import ValidatingGrantHandler
from spresso.model.web.base import Response
from spresso.utils.error import SpressoInvalidError, UnsupportedGrantError
from spresso.utils.log import app_log


class Application(object):
    def __init__(self, response_class=Response):
        self.response_class = response_class
        self.grant_types = []

    def dispatch(self, request, environ):
        try:
            grant_type = self._grant_type(request)
            response = self.response_class()
            if issubclass(grant_type.__class__, ValidatingGrantHandler):
                grant_type.read_validate_params(request)
            return grant_type.process(request, response, environ)
        except SpressoInvalidError as err:
            response = self.response_class()
            return grant_type.handle_error(error=err, response=response)
        except UnsupportedGrantError:
            response = self.response_class()
            response.add_header("Content-Type", "application/json")
            response.status_code = 400
            response.body = json.dumps({
                "error": "unsupported_grant",
                "error_description": "Grant not supported"
            })
            return response
        except:
            app_log.error("Uncaught Exception", exc_info=True)
            response = self.response_class()
            return grant_type.handle_error(
                error=SpressoInvalidError(
                    error="server_error",
                    message="Internal server error"
                ),
                response=response
            )

    def add_grant(self, grant):
        self.grant_types.append(grant)

    def _grant_type(self, request):
        for grant in self.grant_types:
            grant_handler = grant(request, self)
            if grant_handler is not None:
                return grant_handler

        raise UnsupportedGrantError
