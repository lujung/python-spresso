from json import JSONDecodeError
from urllib.parse import unquote

from cryptography.exceptions import InvalidTag, InvalidSignature
from jsonschema import ValidationError

from spresso.controller.grant.authentication.site_adapter.relying_party import \
    IndexSiteAdapter, StartLoginSiteAdapter, \
    RedirectSiteAdapter, LoginSiteAdapter
from spresso.controller.grant.base import GrantHandler, \
    SiteAdapterMixin, ValidatingGrantHandler, JsonErrorMixin
from spresso.model.authentication.identity_assertion import IdentityAssertion
from spresso.model.authentication.request import IdpInfoRequest
from spresso.model.authentication.session import Session
from spresso.model.base import SettingsMixin, Origin, User
from spresso.utils.base import create_nonce, from_b64
from spresso.utils.error import SpressoInvalidError, UnsupportedAdditionalData
from spresso.view.authentication.relying_party import WaitView, \
    StartLoginView, RedirectView, LoginView
from spresso.view.base import View, Script


class IndexHandler(GrantHandler, SiteAdapterMixin, SettingsMixin):
    site_adapter_class = IndexSiteAdapter

    def process(self, request, response, environ):
        script = Script(settings=self.settings)

        self.site_adapter.set_javascript(script.render())
        data = self.site_adapter.render_page(request, response, environ)

        view = View()
        return view.process(data)


class WaitHandler(GrantHandler, SettingsMixin):
    def process(self, request, response, environ):
        view = WaitView(settings=self.settings)
        return view.process(response)


class StartLoginHandler(ValidatingGrantHandler, SiteAdapterMixin,
                        SettingsMixin, JsonErrorMixin):
    site_adapter_class = StartLoginSiteAdapter

    def read_validate_params(self, request):
        self.user = User(
            request.post_param('email'),
            regexp=self.settings.regexp
        )

        if not self.user.is_valid:
            raise SpressoInvalidError(
                error="invalid_request",
                message="Missing or malformed email in request",
                uri=request.path
            )

    def process(self, request, response, environ):
        retriever = IdpInfoRequest(self.user.netloc, settings=self.settings)
        idp_info = retriever.get_content()

        session = Session(self.user, idp_info, settings=self.settings)
        try:
            session.validate()
        except JSONDecodeError:
            raise SpressoInvalidError(
                error="invalid_session",
                message="JSON decoding failed",
                uri=request.path
            )
        except (ValidationError, ValueError) as error:
            raise SpressoInvalidError(
                error="invalid_session",
                message=error,
                uri=request.path
            )

        self.site_adapter.save_session(session)

        view = StartLoginView(session, settings=self.settings)
        return view.process(response)


class RedirectHandler(ValidatingGrantHandler, SiteAdapterMixin,
                      SettingsMixin, JsonErrorMixin):
    site_adapter_class = RedirectSiteAdapter

    def read_validate_params(self, request):
        login_session_token = request.get_param('login_session_token')

        if not login_session_token:
            raise SpressoInvalidError(
                error="invalid_request",
                message="Missing required parameter in request",
                uri=request.path
            )

        self.login_session_token = from_b64(
            unquote(login_session_token),
            return_bytes=True
        )

    def process(self, request, response, environ):
        login_session = self.site_adapter.load_session(
            self.login_session_token
        )

        if not login_session or not isinstance(login_session, Session):
            raise SpressoInvalidError(
                error="invalid_request",
                message="Invalid session",
                uri=request.path
            )

        view = RedirectView(settings=self.settings)

        try:
            login_url = login_session.get_login_url()
        except ValueError as error:
            raise SpressoInvalidError(
                error="invalid_request",
                message=error,
                uri=request.path
            )

        view.template_context = dict(url=login_url)
        return view.process(response)


class LoginHandler(ValidatingGrantHandler, SiteAdapterMixin, SettingsMixin,
                   JsonErrorMixin):
    site_adapter_class = LoginSiteAdapter

    def read_validate_params(self, request):
        login_session_token = request.post_param('login_session_token')
        self.eia = request.post_param('eia')
        origin_header = request.header('Origin')

        if None in [login_session_token, self.eia, origin_header]:
            raise SpressoInvalidError(
                error="invalid_request",
                message="Missing required parameter in request",
                uri=request.path
            )

        self.login_session_token = from_b64(
            login_session_token,
            return_bytes=True
        )

        origin = Origin(origin_header, settings=self.settings)
        if not origin.valid:
            raise SpressoInvalidError(
                error="invalid_request",
                message="Origin request_header mismatch",
                uri=request.path
            )

    def process(self, request, response, environ):
        login_session = self.site_adapter.load_session(
            self.login_session_token
        )

        if not login_session or not isinstance(login_session, Session):
            raise SpressoInvalidError(
                error="invalid_request",
                message="Invalid session",
                uri=request.path
            )

        ia = IdentityAssertion(settings=self.settings)
        ia.from_session(login_session)

        try:
            signature = ia.decrypt(self.eia)
        except JSONDecodeError:
            raise SpressoInvalidError(
                error="invalid_eia",
                message="JSON decoding failed",
                uri=request.path
            )
        except ValueError as error:
            raise SpressoInvalidError(
                error="invalid_eia",
                message=error,
                uri=request.path
            )
        except InvalidTag:
            raise SpressoInvalidError(
                error="invalid_eia",
                message="Decryption of the Identity Assertion failed",
                uri=request.path
            )

        # Extend IA
        additional_data = self.site_adapter.get_additional_data()

        if not isinstance(additional_data, dict):
            raise UnsupportedAdditionalData(
                "Additional data must be of type 'dict'"
            )

        ia.expected_signature.update(additional_data)

        try:
            ia.verify(signature)
        except JSONDecodeError:
            raise SpressoInvalidError(
                error="invalid_signature",
                message="JSON decoding failed",
                uri=request.path
            )
        except ValueError as error:
            raise SpressoInvalidError(
                error="invalid_signature",
                message=error,
                uri=request.path
            )
        except InvalidSignature:
            raise SpressoInvalidError(
                error="invalid_signature",
                message="Identity Assertion signature verification failed",
                uri=request.path
            )

        service_token = create_nonce(32)
        login_session.token = service_token
        self.site_adapter.save_session(login_session)
        response = self.site_adapter.set_cookie(service_token, response)

        view = LoginView(login_session.user.email)
        return view.process(response)
