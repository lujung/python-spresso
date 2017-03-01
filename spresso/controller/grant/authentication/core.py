import spresso.controller.grant.authentication.forward
import spresso.controller.grant.authentication.identity_provider
import spresso.controller.grant.authentication.relying_party
from spresso.controller.grant.authentication.config.forward import \
    Forward
from spresso.controller.grant.authentication.config.identity_provider import \
    IdentityProvider
from spresso.controller.grant.authentication.config.relying_party import \
    RelyingParty
from spresso.controller.grant.base import GrantHandlerFactory, SettingsMixin


class ForwardAuthenticationGrant(GrantHandlerFactory, SettingsMixin):
    settings_class = Forward

    def __call__(self, request, application):
        if request.path == self.settings.endpoints.get('proxy').path and \
           request.method in self.settings.endpoints.get('proxy').methods:
            return spresso.controller.grant.authentication.\
                forward.ProxyHandler(
                    settings=self.settings
                )
        return None


class IdentityProviderAuthenticationGrant(GrantHandlerFactory, SettingsMixin):
    settings_class = IdentityProvider

    def __init__(self, login_site_adapter, signature_site_adapter, **kwargs):
        super(IdentityProviderAuthenticationGrant, self).__init__(**kwargs)
        self.login_site_adapter = login_site_adapter
        self.signature_site_adapter = signature_site_adapter
        self.endpoints = self.settings.endpoints

    def __call__(self, request, application):
        if request.path == self.endpoints.get('info').path and \
           request.method in self.endpoints.get('info').methods:
            return spresso.controller.grant.authentication.\
                identity_provider.InfoHandler(
                    settings=self.settings
                )

        if request.path == self.endpoints.get('login').path and \
           request.method in self.endpoints.get('login').methods:
            return spresso.controller.grant.authentication.\
                identity_provider.LoginHandler(
                    site_adapter=self.login_site_adapter,
                    settings=self.settings
                )

        if request.path == self.endpoints.get('sign').path and \
           request.method in self.endpoints.get('sign').methods:
            return spresso.controller.grant.authentication.\
                identity_provider.SignatureHandler(
                    site_adapter=self.signature_site_adapter,
                    settings=self.settings
                )
        return None


class RelyingPartyAuthenticationGrant(GrantHandlerFactory, SettingsMixin):
    settings_class = RelyingParty

    def __init__(self, index_site_adapter, start_login_site_adapter,
                 redirect_site_adapter, login_site_adapter, **kwargs):
        super(RelyingPartyAuthenticationGrant, self).__init__(**kwargs)
        self.index_site_adapter = index_site_adapter
        self.start_login_site_adapter = start_login_site_adapter
        self.redirect_site_adapter = redirect_site_adapter
        self.login_site_adapter = login_site_adapter
        self.endpoints = self.settings.endpoints

    def __call__(self, request, application):
        if request.path == self.endpoints.get('index').path and \
           request.method in self.endpoints.get('index').methods:
            return spresso.controller.grant.authentication.\
                relying_party.IndexHandler(
                    site_adapter=self.index_site_adapter,
                    settings=self.settings
                )

        if request.path == self.endpoints.get('wait').path and \
           request.method in self.endpoints.get('wait').methods:
            return spresso.controller.grant.authentication.\
                relying_party.WaitHandler(
                    settings=self.settings
                )

        if request.path == self.endpoints.get('start_login').path and \
           request.method in self.endpoints.get('start_login').methods:
            return spresso.controller.grant.authentication.\
                relying_party.StartLoginHandler(
                    site_adapter=self.start_login_site_adapter,
                    settings=self.settings
                )

        if request.path == self.endpoints.get('redirect').path and \
           request.method in self.endpoints.get('redirect').methods:
            return spresso.controller.grant.authentication.\
                relying_party.RedirectHandler(
                    site_adapter=self.redirect_site_adapter,
                    settings=self.settings
                )

        if request.path == self.endpoints.get('login').path and \
           request.method in self.endpoints.get('login').methods:
            return spresso.controller.grant.authentication.\
                relying_party.LoginHandler(
                    site_adapter=self.login_site_adapter,
                    settings=self.settings,
                )
        return None
