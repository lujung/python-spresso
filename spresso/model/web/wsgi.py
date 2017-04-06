from http.cookies import SimpleCookie
from urllib.parse import parse_qs

from spresso.model.web.base import Request


class WsgiRequest(Request):
    """
        Contains data of the current HTTP request.
    """
    def __init__(self, env):
        self.query_params = {}
        self.query_string = env["QUERY_STRING"]
        self.post_params = {}
        self.env_raw = env

        for param, value in parse_qs(env["QUERY_STRING"]).items():
            self.query_params[param] = value[0]

        if self.method == "POST" and \
                self.env_raw["CONTENT_TYPE"].startswith(
                    "application/x-www-form-urlencoded"
                ):
            self.post_params = {}
            content = self.env_raw['wsgi.input'].read(
                int(self.env_raw['CONTENT_LENGTH']))
            post_params = parse_qs(content)

            for param, value in post_params.items():
                decoded_param = param.decode('utf-8')
                decoded_value = value[0].decode('utf-8')
                self.post_params[decoded_param] = decoded_value

    @property
    def method(self):
        """
            Returns the method of the request.
            
            Returns:
                str: The method.
        """
        return self.env_raw["REQUEST_METHOD"]

    @property
    def path(self):
        """
            Returns the path of the request.
            
            Returns:
                str: The path.
        """
        return self.env_raw["PATH_INFO"]

    def get_param(self, name, default=None):
        """
            Returns a param of a GET request identified by its name.
            
            Returns:
                A default value or the parameter.
        """
        try:
            return self.query_params[name]
        except KeyError:
            return default

    def post_param(self, name, default=None):
        """
            Returns a param of a POST request identified by its name.
            
            Returns:
                A default value or the parameter.
        """
        try:
            return self.post_params[name]
        except KeyError:
            return default

    def header(self, name, default=None):
        """
            Returns the value of the HTTP header identified by `name`.
            
            Returns:
                A default value or the header.
        """
        wsgi_header = "HTTP_{0}".format(name.upper())

        try:
            return self.env_raw[wsgi_header]
        except KeyError:
            return default

    @property
    def cookies(self):
        """
            Returns all cookies of the request.
            
            Returns:
                An empty dictionary or all dictionary containing all cookies.
        """
        cookie_string = self.header("Cookie")
        if cookie_string is None:
            return {}

        cookie = SimpleCookie()
        cookie.load(cookie_string)

        # Construct dict from morsel
        cookies = {}
        for key, morsel in cookie.items():
            cookies[key] = morsel.value

        return cookies

    def get_cookie(self, key):
        """
            Returns a specific cookie of the request.
            
            Returns:
                None or the cookie value.
        """
        session_cookie = self.cookies.get(key)

        if session_cookie is None:
            return None

        return session_cookie
