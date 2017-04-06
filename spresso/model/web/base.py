from http.cookies import SimpleCookie


class Request(object):
    """
        Base class defining the interface of a request.
    """
    @property
    def method(self):
        """
            Returns the HTTP method of the request.
        """
        raise NotImplementedError

    @property
    def path(self):
        """
            Returns the current path portion of the current uri.
            Used by some grants to determine which action to take.
        """
        raise NotImplementedError

    def get_param(self, name, default=None):
        """
            Retrieve a parameter from the query string of the request.
        """
        raise NotImplementedError

    def post_param(self, name, default=None):
        """
            Retrieve a parameter from the body of the request.
        """
        raise NotImplementedError

    def header(self, name, default=None):
        """
            Retrieve a header of the request.
        """
        raise NotImplementedError

    @property
    def cookies(self):
        """
            Retrieve a list of cookies from the header of the request.
        """
        raise NotImplementedError

    def get_cookie(self, key):
        """
            Retrieve a specific cookie from the header of the request.
        """
        raise NotImplementedError


class Response(object):
    """
        Contains data returned to the requesting user agent.
    """
    def __init__(self):
        self.status_code = 200
        self._headers = {"Content-Type": "text/html; charset=utf-8"}
        self.data = ""

    @property
    def headers(self):
        """
            Return the headers of the response.
            
            Returns:   
                dict: The headers.
        """
        return self._headers

    def add_header(self, header, value):
        """
            Add a header to the response.
            
            Args:
                header(str): The identifier.
                value(str): The value.
        """
        self._headers[header] = str(value)

    def set_cookie(self, key, value, expires="", path="", comment="", domain="",
                   max_age="", secure=True, version="", http_only=True):
        """
            Add a cookie to the response.
            
            Args:
                key(str): The identifier.
                value(str): The value.
                expires(str): The expiration date.
                path(str): The path.
                comment(str): A comment.
                domain(str): The domain.
                max_age(str): The expiration time in seconds.
                secure(bool): Secure flag.
                version(str): The version.
                http_only(bool): HTTPOnly flag.
                
        """
        c = SimpleCookie()
        c[key] = value
        c[key]['expires'] = expires
        c[key]['path'] = path
        c[key]['comment'] = comment
        c[key]['domain'] = domain
        c[key]['max-age'] = max_age
        c[key]['secure'] = secure
        c[key]['version'] = version
        c[key]['httponly'] = http_only

        header_key, header_value = str(c).split(": ")
        self.add_header(header_key, header_value)
