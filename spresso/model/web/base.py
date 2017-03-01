from http.cookies import SimpleCookie


class Request(object):
    @property
    def method(self):
        raise NotImplementedError

    @property
    def path(self):
        raise NotImplementedError

    def get_param(self, name, default=None):
        raise NotImplementedError

    def post_param(self, name, default=None):
        raise NotImplementedError

    def header(self, name, default=None):
        raise NotImplementedError

    @property
    def cookies(self):
        raise NotImplementedError

    def get_cookie(self, key):
        raise NotImplementedError


class Response(object):
    def __init__(self):
        self.status_code = 200
        self._headers = {"Content-Type": "text/html; charset=utf-8"}
        self.data = ""

    @property
    def headers(self):
        return self._headers

    def add_header(self, header, value):
        self._headers[header] = str(value)

    def set_cookie(self, key, value, expires="", path="", comment="", domain="",
                   max_age="", secure=True, version="", http_only=True):
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
