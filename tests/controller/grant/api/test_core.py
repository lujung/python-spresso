import unittest

from spresso.controller.application import Application
from spresso.controller.grant.api.core import ApiInformation
from spresso.controller.grant.api.settings import ApiInformationSettings
from spresso.controller.grant.base import GrantHandler
from spresso.model.web.wsgi import WsgiRequest


class CoreTestCase(unittest.TestCase):
    def test_api_information(self):
        settings = ApiInformationSettings()
        grant = ApiInformation(settings=settings)

        application = Application()
        application.add_grant(grant)

        self.check_call(grant, application)

    def check_call(self, grant, application):
        for grant in application.grant_types:
            for key, endpoint in grant.settings.endpoints.all().items():
                for method in endpoint.methods:
                    environment = {
                        "REQUEST_METHOD": method,
                        "QUERY_STRING": "",
                        "PATH_INFO": endpoint.path,
                    }
                    if method == "POST":
                        environment.update({"CONTENT_TYPE": ""})

                    request = WsgiRequest(environment)
                    response = grant(request, application)
                    self.assertNotEqual(None, response)
                    self.assertIsInstance(response, GrantHandler)

        environment = {
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "",
            "PATH_INFO": "/test",
        }
        request = WsgiRequest(environment)
        response = grant(request, application)
        self.assertEqual(None, response)
