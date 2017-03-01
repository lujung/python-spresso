from spresso.controller.grant.authentication.site_adapter.identity_provider import LoginSiteAdapter, \
    SignatureSiteAdapter
from spresso.controller.grant.base import GrantHandler, \
    SiteAdapterMixin, ValidatingGrantHandler, JsonErrorMixin
from spresso.model.authentication.identity_assertion import IdentityAssertion
from spresso.model.base import SettingsMixin, Origin, User

from spresso.utils.error import SpressoInvalidError, UserNotAuthenticated, \
    UnsupportedAdditionalData
from spresso.view.authentication.identity_provider import WellKnownInfoView, \
    SignatureView
from spresso.view.base import View, Script


class InfoHandler(GrantHandler, SettingsMixin,
                  JsonErrorMixin):
    def process(self, request, response, environ):
        view = WellKnownInfoView(settings=self.settings)
        return view.process(response)


class LoginHandler(GrantHandler, SiteAdapterMixin,
                   SettingsMixin, JsonErrorMixin):
    site_adapter_class = LoginSiteAdapter

    def process(self, request, response, environ):
        user = self.site_adapter.authenticate_user(request, response, environ)

        if user:
            if not isinstance(user, User):
                raise ValueError("authenticate_user must return an instance of "
                                 "class '{0}'".format(User))
            email = user.email
        else:
            email = ""

        script = Script(self.settings)
        script.template_context.update(dict(email=email))

        self.site_adapter.set_javascript(script.render())
        data = self.site_adapter.render_page(request, response, environ)

        view = View()
        return view.process(data)


class SignatureHandler(ValidatingGrantHandler, SiteAdapterMixin,
                       SettingsMixin, JsonErrorMixin):
    site_adapter_class = SignatureSiteAdapter

    def read_validate_params(self, request):
        email = request.post_param('email')
        tag = request.post_param('tag')
        forwarder_domain = request.post_param('forwarder_domain')
        origin_header = request.header('Origin')

        if not all([email, tag, forwarder_domain, origin_header]):
            raise SpressoInvalidError(
                error="invalid_request",
                message="Missing required parameter in request",
                uri=request.path
            )

        origin = Origin(origin_header, settings=self.settings)
        if not origin.valid:
            raise SpressoInvalidError(
                error="invalid_request",
                message="Origin header mismatch",
                uri=request.path
            )

    def process(self, request, response, environ):
        try:
            self.site_adapter.authenticate_user(request, response, environ)
        except UserNotAuthenticated as auth_error:
            raise SpressoInvalidError(
                error="auth_failed",
                message="{0!s}".format(auth_error),
                uri=request.path
            )

        ia = IdentityAssertion(settings=self.settings)
        ia.from_request(request)

        # extend IA
        additional_data = self.site_adapter.get_additional_data()

        if not isinstance(additional_data, dict):
            raise UnsupportedAdditionalData(
                "Additional data must be of type 'dict'")

        ia.signature.update(additional_data)

        try:
            signature = ia.sign()
        except ValueError as error:
            raise SpressoInvalidError(
                error="invalid_request",
                message=error,
                uri=request.path
            )

        view = SignatureView(signature, settings=self.settings)
        return view.process(response)
