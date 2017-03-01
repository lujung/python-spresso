from spresso.model.web.wsgi import WsgiRequest


def in_supported_endpoints(endpoints, environ):
    def f(x):
        return environ['PATH_INFO'] == x.path and \
               environ['REQUEST_METHOD'] in x.methods

    return any(map(f, endpoints.values()))


class WsgiApplication(object):
    """
    Implements WSGI.
    """
    HTTP_CODES = {200: "200 OK",
                  301: "301 Moved Permanently",
                  302: "302 Found",
                  400: "400 Bad Request",
                  401: "401 Unauthorized",
                  404: "404 Not Found",
                  405: "405 Method not allowed"}

    def __init__(self, application):
        self.application = application
        self.endpoints = dict()
        for grant in application.grant_types:
            self.endpoints.update(grant.settings.endpoints.all())

    def __call__(self, environ, start_response):
        if not self.endpoints or \
                not in_supported_endpoints(self.endpoints, environ):
            start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
            return [b'Not Found']

        request = WsgiRequest(environ)

        response = self.application.dispatch(request, environ)

        start_response(self.HTTP_CODES[response.status_code],
                       list(response.headers.items()))

        return [response.data.encode('utf-8')]


class PathDispatcher(object):
    def __init__(self, default_app, app):
        self.default_app = default_app

        if not isinstance(app, WsgiApplication):
            raise ValueError("'app' must be of type {0}".format(
                WsgiApplication.__name__)
            )
        self.app = app

    def get_application(self, environ):
        if in_supported_endpoints(self.app.endpoints, environ):
            return self.app
        return None

    def __call__(self, environ, start_response):
        app = self.get_application(environ)

        if app is None:
            app = self.default_app

        return app(environ, start_response)
