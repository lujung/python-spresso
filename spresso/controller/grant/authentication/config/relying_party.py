from spresso.controller.grant.settings import Setting
from spresso.model.authentication.json_schema import StartLoginDefinition, \
    IdentityAssertionDefinition, WellKnownInfoDefinition
from spresso.model.cache import Cache
from spresso.model.settings import Container, Schema, Endpoint, \
    SelectionContainer, CachingSetting, ForwardDomain


class RelyingParty(Setting):
    resource_path = "resources/authentication/"
    regexp = r"^[^#&]+@([a-zA-Z0-9-.]+)$"

    js_template = "script/rp.js"
    wait_template = "html/wait.html"
    redirect_template = "html/redir.html"

    json_schemata = Container(
        Schema("start_login", StartLoginDefinition()),
        Schema("ia_signature", IdentityAssertionDefinition()),
        Schema("info", WellKnownInfoDefinition())
    )

    endpoints = Container(
        Endpoint("index", "/", ["GET", "POST"]),
        Endpoint("wait", "/wait", ["GET"]),
        Endpoint("start_login", "/startLogin", ["POST"]),
        Endpoint("redirect", "/redir", ["GET"]),
        Endpoint("login", "/login", ["POST"]),
    )

    default_idp_endpoints = Container(
        Endpoint("info", "/.well-known/spresso-info", ["GET"]),
        Endpoint("login", "/.well-known/spresso-login", ["GET", "POST"]),
        name="default"
    )
    endpoints_ext = SelectionContainer("select", default=default_idp_endpoints)

    # CachingSetting container for the well known info on multiple idps
    default_caching = CachingSetting("default", True, 48 * 60 * 60)
    caching_settings = SelectionContainer("select", default=default_caching)

    fwd_selector = SelectionContainer("random")

    # Requests are done by the requests package,
    # refer to its documentation on 'proxies' and 'verify'
    proxies = {}
    verify = True

    def __init__(self, domain, forwarder_domain):
        super(RelyingParty, self).__init__()
        self.domain = domain
        self.fwd_selector.update_default(
            ForwardDomain("default", forwarder_domain)
        )
        self.scheme_well_known_info = self.scheme
        self.cache = Cache(self)
