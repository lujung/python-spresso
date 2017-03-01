import unittest
from unittest.mock import Mock, MagicMock, PropertyMock, patch

from spresso.controller.grant.authentication.identity_provider import \
    InfoHandler, LoginHandler, SignatureHandler
from spresso.controller.grant.authentication.site_adapter.identity_provider \
    import LoginSiteAdapter, SignatureSiteAdapter
from spresso.model.base import User
from spresso.model.web.base import Response
from spresso.model.web.wsgi import WsgiRequest
from spresso.utils.error import UserNotAuthenticated, SpressoInvalidError, \
    UnsupportedAdditionalData
from spresso.view.base import Script


class IdentityProviderAuthenticationGrantTestCase(unittest.TestCase):
    @patch("spresso.controller.grant.authentication.identity_provider."
           "WellKnownInfoView")
    def test_info_handler(self, view_mock):
        view = Mock()
        view_mock.return_value = view

        settings = Mock()
        handler = InfoHandler(settings=settings)

        request = Mock()
        response = Mock()
        environ = Mock()

        # Test process
        handler.process(request, response, environ)

        view_mock.assert_called_once_with(settings=settings)
        view.process.assert_called_once_with(response)

    @patch("spresso.controller.grant.authentication.identity_provider.View")
    @patch("spresso.controller.grant.authentication.identity_provider.Script")
    def test_login_handler(self, script_mock, view_mock):
        login_site_adapter = Mock(spec=LoginSiteAdapter)
        user = "user"
        login_site_adapter.authenticate_user.return_value = user
        data = "data"
        login_site_adapter.render_page.return_value = data

        view = Mock()
        view_mock.return_value = view

        script = MagicMock(spec=Script)
        script.render.return_value = "script"
        context = PropertyMock()
        script.template_context = context
        script_mock.return_value = script

        settings = Mock()

        handler = LoginHandler(
            site_adapter=login_site_adapter,
            settings=settings
        )

        request = Mock()
        response = Mock()
        environ = Mock()

        self.assertRaises(
            ValueError,
            handler.process,
            request,
            response,
            environ
        )

        user = Mock(spec=User)
        user_email = Mock()
        user.email = user_email
        login_site_adapter.authenticate_user.return_value = user
        login_site_adapter.reset_mock()

        # Test process
        handler.process(request, response, environ)

        login_site_adapter.authenticate_user.assert_called_once_with(
            request,
            response,
            environ
        )
        script_mock.assert_called_once_with(settings)
        context.update.assert_called_once_with(dict(email=user_email))
        self.assertEqual(script.render.call_count, 1)
        login_site_adapter.set_javascript.assert_called_once_with("script")
        login_site_adapter.render_page.assert_called_once_with(
            request,
            response,
            environ
        )

        self.assertEqual(view_mock.call_count, 1)
        view.process.assert_called_once_with(data)

    @patch("spresso.controller.grant.authentication.identity_provider.Origin")
    @patch("spresso.controller.grant.authentication.identity_provider."
           "IdentityAssertion")
    @patch("spresso.controller.grant.authentication.identity_provider."
           "SignatureView")
    def test_signature_handler(self, view_mock, ia_mock, origin_mock):
        view = Mock()
        view_mock.return_value = view

        signature_site_ad = Mock(spec=SignatureSiteAdapter)
        settings = Mock()

        origin = Mock()
        origin.valid = False
        origin_mock.return_value = origin

        handler = SignatureHandler(
            site_adapter=signature_site_ad,
            settings=settings
        )

        content_length = "42"
        request_method = "POST"
        query_string = ""
        content = "email=email&tag=tag&forwarder_domain=fwd".encode('utf-8')

        wsgi_input_mock = Mock(spec=["read"])
        wsgi_input_mock.read.return_value = content
        origin_header = "origin"

        environment = {
            "CONTENT_LENGTH": content_length,
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "REQUEST_METHOD": request_method,
            "QUERY_STRING": query_string,
            "HTTP_ORIGIN": origin_header,
            "PATH_INFO": "/",
            "wsgi.input": wsgi_input_mock
        }

        request = WsgiRequest(environment)
        response = Response()
        environ = ""

        self.assertRaises(
            SpressoInvalidError,
            handler.read_validate_params,
            request
        )
        origin_mock.reset_mock()
        origin.valid = True

        # Test validate
        handler.read_validate_params(request)
        origin_mock.assert_called_once_with(origin_header, settings=settings)

        signature_site_ad.authenticate_user.side_effect = UserNotAuthenticated
        self.assertRaises(
            SpressoInvalidError,
            handler.process,
            request,
            response,
            environ
        )
        signature_site_ad.authenticate_user.side_effect = None

        ia = Mock()
        signature = Mock()
        ia.sign.return_value = signature
        ia_signed_json = Mock()
        ia.signature_json.return_value = ia_signed_json
        ia_mock.return_value = ia

        handler = SignatureHandler(
            site_adapter=signature_site_ad,
            settings=settings,
        )

        additional_data = {}
        signature_site_ad.get_additional_data.return_value = "test"

        self.assertRaises(
            UnsupportedAdditionalData,
            handler.process,
            request,
            response,
            environ
        )

        signature_site_ad.get_additional_data.return_value = additional_data

        ia.sign.side_effect = ValueError

        self.assertRaises(
            SpressoInvalidError,
            handler.process,
            request,
            response,
            environ
        )
        ia.sign.side_effect = None
        ia_mock.reset_mock()
        ia.reset_mock()
        signature_site_ad.reset_mock()

        # Test process
        handler.process(request, response, environ)

        signature_site_ad.authenticate_user.assert_called_once_with(
            request, response, environ
        )
        ia_mock.assert_called_once_with(settings=settings)
        ia.from_request.assert_called_once_with(request)
        self.assertEqual(signature_site_ad.get_additional_data.call_count, 1)
        ia.signature.update.assert_called_once_with(additional_data)
        self.assertEqual(ia.sign.call_count, 1)

        view_mock.assert_called_once_with(signature, settings=settings)
        view.process.assert_called_once_with(response)
