class UserFacingSiteAdapter(object):
    def render_page(self, request, response, environ):
        raise NotImplementedError


class JavascriptSiteAdapter(object):
    def set_javascript(self, script):
        raise NotImplementedError


class AuthenticatingSiteAdapter(object):
    def authenticate_user(self, request, response, environ):
        raise NotImplementedError


class IdentityAssertionExtensionSiteAdapter(object):
    def get_additional_data(self):
        return dict()


class SessionSaveSiteAdapter(object):
    def save_session(self, session):
        raise NotImplementedError


class SessionLoadSiteAdapter(object):
    def load_session(self, key):
        raise NotImplementedError


class CookieSiteAdapter(object):
    def set_cookie(self, service_token, response):
        raise NotImplementedError
