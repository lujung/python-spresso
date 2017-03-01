from spresso.controller.grant.authentication.site_adapter.base import \
    UserFacingSiteAdapter, JavascriptSiteAdapter, AuthenticatingSiteAdapter, \
    IdentityAssertionExtensionSiteAdapter


class LoginSiteAdapter(UserFacingSiteAdapter, JavascriptSiteAdapter,
                       AuthenticatingSiteAdapter):
    pass


class SignatureSiteAdapter(AuthenticatingSiteAdapter,
                           IdentityAssertionExtensionSiteAdapter):
    pass
