import logging
from wsgiref.simple_server import make_server

from spresso.controller.application import Application
from spresso.controller.grant.authentication.config.identity_provider import \
    IdentityProvider
from spresso.controller.grant.authentication.core import \
    IdentityProviderAuthenticationGrant
from spresso.controller.grant.authentication.site_adapter. \
    identity_provider import LoginSiteAdapter, SignatureSiteAdapter
from spresso.controller.web.wsgi import WsgiApplication
from spresso.model.base import User
from spresso.utils.base import from_b64, create_nonce, to_b64
from spresso.utils.error import UserNotAuthenticated

users = {
    "foo@127.0.0.1:8080": dict(
        password="bar"
    )
}
sessions = dict()

logging.basicConfig(level=logging.DEBUG)


class ExampleLoginSiteAdapter(LoginSiteAdapter):
    TEMPLATE = '''
    <html>
        <head>
            <script type="text/javascript">
            {}
            function loginFailed(response) {{
                alert('Server responded: ' + response.responseText);
            }}
            </script>
        </head>
        <body>
        <form id='loginform' onsubmit="getIdentityAssertion(); return false;">
        Email Address: <span id="email"></span><br>
        Password:<input type="password" id="password">
        <button type="submit">Log In</button>
        </form>
        </body>
    </html>
    '''

    def set_javascript(self, script):
        # Receive the JavaScript
        self.script = script

    def authenticate_user(self, request, response, environ):
        # Return User object, if the user is already logged in
        session_cookie = request.get_cookie("idp_session")
        if session_cookie:
            session_cookie = from_b64(session_cookie, return_bytes=True)
        email = sessions.get(session_cookie)
        if email:
            return User(email)
        return None

    def render_page(self, request, response, environ):
        # Embed the JavaScript into your view
        response.data = self.TEMPLATE.format(self.script)
        return response


class ExampleSignatureSiteAdapter(SignatureSiteAdapter):
    def authenticate_user(self, request, response, environ):
        # Raise UserNotAuthenticated("message") Exception if the user could not
        # be authenticated locally.
        # POST parameter are accessible through the request object:
        email = request.post_param('email')
        password = request.post_param('password')
        session_cookie = request.get_cookie("idp_session")

        if session_cookie:
            session_cookie = from_b64(session_cookie, return_bytes=True)
        logged_in_as = sessions.get(session_cookie)

        if email is not None:
            if email == logged_in_as:
                # User is already logged in
                return

            if password is not None:
                # Place your login handler here
                if email in users:
                    if users.get(email).get('password') == password:
                        session_nonce = create_nonce(32)
                        sessions.update({session_nonce: email})
                        return response.set_cookie(
                            'idp_session',
                            to_b64(session_nonce),
                            secure=False,
                            http_only=False
                        )

        # User could not be authenticated
        raise UserNotAuthenticated("Authentication failed")


# Create config
domain = "127.0.0.1:8080"
private_key_path = "priv_key"
public_key_path = "pub_key"
settings = IdentityProvider(domain, private_key_path, public_key_path)
settings.scheme = "http"

# Create the controller
application = Application()
application.add_grant(
    IdentityProviderAuthenticationGrant(
        login_site_adapter=ExampleLoginSiteAdapter(),
        signature_site_adapter=ExampleSignatureSiteAdapter(),
        settings=settings
    )
)

# Wrap the controller with the WSGI adapter
app = WsgiApplication(application)

if __name__ == "__main__":
    httpd = make_server('', 8080, app)
    httpd.serve_forever()
