import unittest
from json import JSONDecodeError
from unittest.mock import Mock, patch, ANY, MagicMock

from cryptography.exceptions import InvalidTag, InvalidSignature
from jsonschema import ValidationError

from spresso.controller.grant.authentication.relying_party import \
    IndexHandler, WaitHandler, \
    StartLoginHandler, RedirectHandler, \
    LoginHandler
from spresso.controller.grant.authentication.site_adapter.relying_party import \
    IndexSiteAdapter, StartLoginSiteAdapter, \
    RedirectSiteAdapter, LoginSiteAdapter
from spresso.model.authentication.session import Session
from spresso.utils.error import UnsupportedAdditionalData, \
    SpressoInvalidError


class RelyingPartyAuthenticationGrantTestCase(unittest.TestCase):
    @patch("spresso.controller.grant.authentication.relying_party.Script")
    @patch("spresso.controller.grant.authentication.relying_party.View")
    def test_index_handler(self, view_mock, script_mock):
        view = Mock()
        view_mock.return_value = view

        index_site_adapter = Mock(spec=IndexSiteAdapter)
        data = "data"
        index_site_adapter.render_page.return_value = data
        settings = Mock()

        script = Mock()
        script.render.return_value = "script"
        script_mock.return_value = script

        handler = IndexHandler(
            site_adapter=index_site_adapter,
            settings=settings
        )

        request = Mock()
        response = Mock()
        environ = Mock()

        handler.process(request, response, environ)

        script_mock.assert_called_once_with(settings=settings)
        self.assertEqual(script.render.call_count, 1)
        index_site_adapter.set_javascript.assert_called_once_with("script")
        index_site_adapter.render_page.assert_called_once_with(
            request,
            response,
            environ
        )

        self.assertEqual(view_mock.call_count, 1)
        view.process.assert_called_once_with(data)

    @patch("spresso.controller.grant.authentication.relying_party.WaitView")
    def test_wait_handler(self, view_mock):
        view = Mock()
        view_mock.return_value = view
        settings = Mock()

        handler = WaitHandler(settings=settings)
        request = Mock()
        response = Mock()
        environ = Mock()

        handler.process(request, response, environ)
        view_mock.assert_called_once_with(settings=settings)
        view.process.assert_called_once_with(response)

    @patch("spresso.controller.grant.authentication.relying_party.User")
    @patch(
        "spresso.controller.grant.authentication.relying_party.IdpInfoRequest")
    @patch("spresso.controller.grant.authentication.relying_party.Session")
    @patch(
        "spresso.controller.grant.authentication.relying_party.StartLoginView")
    def test_start_login_handler(self, view_mock, session_mock, retriever_mock,
                                 user_mock):
        view = Mock()
        view_mock.return_value = view

        start_login_site_adapter = Mock(spec=StartLoginSiteAdapter)
        settings = Mock()
        settings.regexp = "r"

        user = Mock()
        netloc = Mock()
        user.netloc = netloc
        user_mock.return_value = user

        retriever = Mock()
        idp_info_mock = Mock()
        retriever_mock.return_value = retriever
        retriever.get_content.return_value = idp_info_mock

        session = Mock()
        session.token = "token"
        session_mock.return_value = session

        handler = StartLoginHandler(
            site_adapter=start_login_site_adapter,
            settings=settings
        )

        email = "email@test"
        request = Mock()
        request.post_param.return_value = email
        response = Mock()
        environ = Mock()

        # Test validate
        user.is_valid = False
        self.assertRaises(
            SpressoInvalidError,
            handler.read_validate_params,
            request
        )
        user.is_valid = True
        user_mock.reset_mock()

        handler.read_validate_params(request)
        user_mock.assert_called_once_with(email, regexp="r")

        # Test process

        for error in [
            JSONDecodeError("test", "", 0),
            ValidationError("test"),
            ValueError
        ]:
            session.validate.side_effect = error
            self.assertRaises(
                SpressoInvalidError,
                handler.process,
                request,
                response,
                environ
            )

        session.validate.side_effect = None
        retriever_mock.reset_mock()
        retriever.reset_mock()
        session_mock.reset_mock()
        session.reset_mock()

        handler.process(request, response, environ)

        retriever_mock.assert_called_once_with(netloc, settings=settings)
        self.assertEqual(retriever.get_content.call_count, 1)
        session_mock.assert_called_once_with(
            user,
            idp_info_mock,
            settings=settings
        )
        start_login_site_adapter.save_session.assert_called_once_with(
            session
        )
        view_mock.assert_called_once_with(session, settings=settings)
        view.process.assert_called_once_with(response)

    @patch("spresso.controller.grant.authentication.relying_party.from_b64")
    @patch("spresso.controller.grant.authentication.relying_party.unquote")
    @patch("spresso.controller.grant.authentication.relying_party.RedirectView")
    def test_redirect_handler(self, view_mock, unquote_mock, b64_mock):
        view = Mock()
        view_mock.return_value = view

        redirect_site_adapter = Mock(spec=RedirectSiteAdapter)

        settings = Mock()

        handler = RedirectHandler(
            site_adapter=redirect_site_adapter,
            settings=settings
        )

        request = Mock()
        request.get_param.return_value = ""
        response = Mock()
        environ = Mock()

        self.assertRaises(
            SpressoInvalidError,
            handler.read_validate_params,
            request
        )
        request.get_param.return_value = "token"
        b64_mock.return_value = "token"
        unquote_mock.return_value = "unquoted token"

        handler.read_validate_params(request)

        b64_mock.assert_called_once_with("unquoted token", return_bytes=True)
        self.assertEqual(handler.login_session_token, "token")

        # Test process
        for value in ["", Mock()]:
            redirect_site_adapter.load_session.return_value = value
            self.assertRaises(
                SpressoInvalidError,
                handler.process,
                request,
                response,
                environ
            )
        redirect_site_adapter.reset_mock()

        session = Mock(spec=Session)
        redirect_site_adapter.load_session.return_value = session

        session.get_login_url.side_effect = ValueError
        self.assertRaises(
            SpressoInvalidError,
            handler.process,
            request,
            response,
            environ
        )
        session.get_login_url.side_effect = None
        session.reset_mock()
        redirect_site_adapter.reset_mock()
        view_mock.reset_mock()

        session.get_login_url.return_value = "login url"
        view.process.return_value = "return"
        res = handler.process(request, response, environ)

        redirect_site_adapter.load_session.assert_called_once_with(
            "token"
        )
        view_mock.assert_called_once_with(settings=settings)
        self.assertEqual(session.get_login_url.call_count, 1)
        self.assertEqual(view.template_context, dict(url="login url"))
        view.process.assert_called_once_with(response)
        self.assertEqual(res, "return")

    @patch("spresso.controller.grant.authentication.relying_party.from_b64")
    @patch("spresso.controller.grant.authentication.relying_party.Origin")
    @patch("spresso.controller.grant.authentication.relying_party.LoginView")
    @patch("spresso.controller.grant.authentication.relying_party."
           "IdentityAssertion")
    def test_login_handler(self, ia_mock, view_mock, origin_mock, b64_mock):
        view = Mock()
        view_mock.return_value = view

        # read_validate_params
        login_site_adapter = Mock(spec=LoginSiteAdapter)
        settings = Mock()

        handler = LoginHandler(
            site_adapter=login_site_adapter,
            settings=settings
        )

        request = Mock()
        request.post_param = post_param_none
        request.header = request_header
        response = Mock()
        environ = Mock()

        self.assertRaises(
            SpressoInvalidError,
            handler.read_validate_params,
            request
        )

        request.post_param = post_param_mock
        b64_mock.return_value = "token"
        origin = Mock()
        origin.valid = False
        origin_mock.return_value = origin

        self.assertRaises(
            SpressoInvalidError,
            handler.read_validate_params,
            request
        )

        b64_mock.reset_mock()
        origin_mock.reset_mock()
        origin.valid = True

        handler.read_validate_params(request)

        b64_mock.assert_called_once_with(
            "login_session_token",
            return_bytes=True
        )
        origin_mock.assert_called_once_with("Origin", settings=settings)

        # Test process
        for value in ["", Mock()]:
            login_site_adapter.load_session.return_value = value
            self.assertRaises(
                SpressoInvalidError,
                handler.process,
                request,
                response,
                environ
            )

        session = Mock(spec=Session)
        login_site_adapter.load_session.return_value = session

        ia = MagicMock()
        ia_mock.return_value = ia

        for effect in [
            JSONDecodeError("test", "", 0),
            ValueError,
            InvalidTag
        ]:
            ia.decrypt.side_effect = effect
            self.assertRaises(
                SpressoInvalidError,
                handler.process,
                request,
                response,
                environ
            )
        ia.decrypt.side_effect = None

        login_site_adapter.get_additional_data.return_value = "test"
        self.assertRaises(
            UnsupportedAdditionalData,
            handler.process,
            request,
            response,
            environ
        )
        additional_data = {}
        login_site_adapter.get_additional_data.return_value = additional_data

        for effect in [
            JSONDecodeError("test", "", 0),
            ValueError,
            InvalidSignature
        ]:
            ia.verify.side_effect = effect
            self.assertRaises(
                SpressoInvalidError,
                handler.process,
                request,
                response,
                environ
            )
        ia.verify.side_effect = None

        login_site_adapter.reset_mock()
        ia_mock.reset_mock()
        ia.reset_mock()
        ex_sig = Mock()
        ia.expected_signature = ex_sig
        ia.decrypt.return_value = "signature"
        user = Mock()
        user.email = "email"
        session.user = user
        login_site_adapter.set_cookie.return_value = "response"
        view.process.return_value = "res"

        res = handler.process(request, response, environ)

        login_site_adapter.load_session.assert_called_once_with(
            "token"
        )
        ia_mock.assert_called_once_with(settings=settings)
        ia.from_session.assert_called_once_with(session)
        self.assertEqual(
            login_site_adapter.get_additional_data.call_count,
            1
        )
        ex_sig.update.assert_called_once_with(additional_data)
        ia.verify.assert_called_once_with("signature")
        login_site_adapter.save_session.assert_called_once_with(
            session
        )
        login_site_adapter.set_cookie.assert_called_once_with(
            ANY,
            response
        )
        view_mock.assert_called_once_with("email")
        view.process.assert_called_once_with("response")
        self.assertEqual(res, "res")


def post_param_mock(arg):
    return arg


def post_param_none(arg):
    return None


def request_header(arg):
    return arg
