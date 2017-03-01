import logging
from wsgiref.simple_server import make_server

from spresso.controller.application import Application
from spresso.controller.grant.authentication.core import \
    ForwardAuthenticationGrant
from spresso.controller.grant.authentication.config.forward import \
    Forward
from spresso.controller.web.wsgi import WsgiApplication

logging.basicConfig(level=logging.DEBUG)

# Create config
settings = Forward()
settings.scheme = "http"

# Create the controller
application = Application()
application.add_grant(ForwardAuthenticationGrant(settings=settings))

# Wrap the controller with the WSGI adapter
app = WsgiApplication(application)

if __name__ == "__main__":
    httpd = make_server('', 8081, app)
    httpd.serve_forever()
