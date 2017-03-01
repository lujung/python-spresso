import logging
from wsgiref.simple_server import make_server

from spresso.controller.application import Application
from spresso.controller.grant.api.core import ApiInformation
from spresso.controller.grant.api.settings import ApiInformationSettings
from spresso.controller.grant.authentication.config.relying_party import \
    RelyingParty
from spresso.controller.grant.authentication.core import \
    RelyingPartyAuthenticationGrant
from spresso.controller.grant.authentication.site_adapter.relying_party import \
    IndexSiteAdapter, StartLoginSiteAdapter, RedirectSiteAdapter, \
    LoginSiteAdapter
from spresso.controller.web.wsgi import WsgiApplication
from spresso.utils.base import to_b64

sessions = dict()
authenticated_sessions = dict()

logging.basicConfig(level=logging.DEBUG)


class ExampleIndexSiteAdapter(IndexSiteAdapter):
    TEMPLATE = '''
        <html>
            <head>
                <script type="text/javascript">
                {}
                function loginSuccessful(response) {{
                    alert('Congratulations, you are logged in with ' +
                    response.responseText + '. Have fun.');
                }}
                function loginFailed(response) {{
                    alert('Server responded: ' + response.responseText);
                }}
                function startLoginFailed(response) {{
                    alert('Server responded: ' + response.responseText);
                }}
                </script>
            </head>
            <body>
                <form onsubmit="startLogin(); return false;">
                    <input id="email_input" value="" required autofocus>
                    <button type="submit">Login</button>
                </form>
            </body>
        </html>
    '''

    def set_javascript(self, script):
        # Receive the JavaScript
        self.script = script

    def render_page(self, request, response, environ):
        # Embed the JavaScript into your view
        response.data = self.TEMPLATE.format(self.script)
        return response


class ExampleStartLoginSiteAdapter(StartLoginSiteAdapter):
    def save_session(self, session):
        sessions.update({session.token: session})


class ExampleRedirectSiteAdapter(RedirectSiteAdapter):
    def load_session(self, key):
        return sessions.get(key)


class ExampleLoginSiteAdapter(LoginSiteAdapter):
    def load_session(self, key):
        return sessions.get(key)

    def save_session(self, session):
        authenticated_sessions.update({session.token: session})

    def set_cookie(self, service_token, response):
        # Set client cookie with service_token
        response.set_cookie("rp_session", to_b64(service_token), secure=False,
                            http_only=False)
        return response


# Create config
domain = "127.0.0.1:8082"
forwarder_domain = "127.0.0.1:8081"
settings = RelyingParty(domain, forwarder_domain)

# settings.debug = False
settings.regexp = '.*'
settings.scheme = "http"
settings.scheme_well_known_info = "http"
# settings.caching_settings.update(CachingSetting("default", True, 0))

# Create the controller.
application = Application()
application.add_grant(
    RelyingPartyAuthenticationGrant(
        index_site_adapter=ExampleIndexSiteAdapter(),
        start_login_site_adapter=ExampleStartLoginSiteAdapter(),
        redirect_site_adapter=ExampleRedirectSiteAdapter(),
        login_site_adapter=ExampleLoginSiteAdapter(),
        settings=settings
    )
)

application.add_grant(
    ApiInformation(settings=ApiInformationSettings())
)

# Wrap the controller with he Wsgi adapter
app = WsgiApplication(application)

if __name__ == "__main__":
    httpd = make_server('', 8082, app)
    httpd.serve_forever()
