import unittest
from unittest.mock import Mock, patch

import spresso.controller.grant.authentication.config
import spresso.controller.grant.authentication.site_adapter.identity_provider
from spresso.controller.application import Application
from spresso.controller.grant.authentication.config.forward import Forward
from spresso.controller.grant.authentication.config.identity_provider import \
    IdentityProvider
from spresso.controller.grant.authentication.config.relying_party import \
    RelyingParty
from spresso.controller.grant.authentication.core import \
    ForwardAuthenticationGrant, IdentityProviderAuthenticationGrant, \
    RelyingPartyAuthenticationGrant
from spresso.controller.grant.authentication.site_adapter.relying_party import \
    IndexSiteAdapter, StartLoginSiteAdapter, \
    RedirectSiteAdapter, LoginSiteAdapter
from spresso.controller.grant.base import GrantHandler
from spresso.model.web.wsgi import WsgiRequest


class CoreTestCase(unittest.TestCase):
    def test_forward_authentication_grant(self):
        settings = Forward()
        grant = ForwardAuthenticationGrant(settings=settings)

        application = Application()
        application.add_grant(grant)

        self.check_call(grant, application)

    @patch("spresso.controller.grant.authentication.config.identity_provider."
           "get_file_content")
    def test_identity_provider_authentication_grant(self, get_content_mock):
        login_site_adapter = Mock(
            spec=spresso.controller.grant.authentication.site_adapter.
            identity_provider.LoginSiteAdapter
        )
        signature_site_adapter = Mock(
            spec=spresso.controller.grant.authentication.
            site_adapter.identity_provider.SignatureSiteAdapter
        )

        get_content_mock.return_value = "key"
        settings = IdentityProvider(Mock(), Mock(), Mock())
        grant = IdentityProviderAuthenticationGrant(
            login_site_adapter=login_site_adapter,
            signature_site_adapter=signature_site_adapter,
            settings=settings
        )

        application = Application()
        application.add_grant(grant)

        self.check_call(grant, application)

    def test_relying_party_authentication_grant(self):
        index_site_adapter = Mock(spec=IndexSiteAdapter)
        start_login_site_adapter = Mock(spec=StartLoginSiteAdapter)
        redirect_site_adapter = Mock(spec=RedirectSiteAdapter)
        login_site_adapter = Mock(spec=LoginSiteAdapter)

        settings = RelyingParty(Mock(), Mock())
        grant = RelyingPartyAuthenticationGrant(
            index_site_adapter=index_site_adapter,
            start_login_site_adapter=start_login_site_adapter,
            redirect_site_adapter=redirect_site_adapter,
            login_site_adapter=login_site_adapter,
            settings=settings
        )

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
