from spresso.controller.grant.settings import Setting
from spresso.model.settings import Container, Endpoint


class Forward(Setting):
    resource_path = "resources/authentication/"
    # Javascript
    js_template = "script/fwd.js"
    proxy_template = "html/proxy.html"

    endpoints = Container(
        Endpoint("proxy", "/.well-known/spresso-proxy", ["GET"]),
    )
