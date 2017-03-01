from spresso.controller.grant.settings import Setting
from spresso.model.authentication.json_schema import WellKnownInfoDefinition, \
    IdentityAssertionDefinition
from spresso.model.settings import Container, Schema, Endpoint

from spresso.utils.base import get_file_content


class IdentityProvider(Setting):
    resource_path = "resources/authentication/"
    js_template = "script/idp.js"

    json_schemata = Container(
        Schema("info", WellKnownInfoDefinition()),
        Schema("sign", IdentityAssertionDefinition())
    )

    # Provider URL paths
    endpoints = Container(
        Endpoint("info", "/.well-known/spresso-info", ["GET"]),
        Endpoint("login", "/.well-known/spresso-login", ["GET", "POST"]),
        Endpoint("sign", "/sign", ["POST"]),
    )
    # External URL path
    endpoints_ext = Container(
        Endpoint("proxy", "/.well-known/spresso-proxy", ["GET"])
    )

    # Subresource Integrity
    # Currently not in use, as SRI for iframes is currently under development.
    # This should be used in future versions.
    sri = False
    sri_hash = None

    def __init__(self, domain, private_key_path, public_key_path):
        super(IdentityProvider, self).__init__()
        self.domain = domain
        self.private_key = get_file_content(private_key_path, "rb")
        self.public_key = get_file_content(public_key_path, "r")
