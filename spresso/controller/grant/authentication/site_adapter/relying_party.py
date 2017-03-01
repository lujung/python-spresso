from spresso.controller.grant.authentication.site_adapter.base import \
    UserFacingSiteAdapter, JavascriptSiteAdapter, \
    SessionSaveSiteAdapter, SessionLoadSiteAdapter, \
    CookieSiteAdapter, IdentityAssertionExtensionSiteAdapter


class IndexSiteAdapter(UserFacingSiteAdapter, JavascriptSiteAdapter):
    pass


class StartLoginSiteAdapter(SessionSaveSiteAdapter):
    pass


class RedirectSiteAdapter(SessionLoadSiteAdapter):
    pass


class LoginSiteAdapter(SessionLoadSiteAdapter, SessionSaveSiteAdapter,
                       CookieSiteAdapter,
                       IdentityAssertionExtensionSiteAdapter):
    pass
