from spresso.model.base import JsonSchema


class AuthenticationJsonSchema(JsonSchema):
    resource_path = "resources/authentication/"


class WellKnownInfoDefinition(AuthenticationJsonSchema):
    file_path = "json/wk_info.json"

    public_key = "public_key"


class IdentityAssertionDefinition(AuthenticationJsonSchema):
    file_path = "json/ia_sig.json"

    ia = "ia_signature"


class StartLoginDefinition(AuthenticationJsonSchema):
    file_path = "json/start_login.json"

    forwarder_domain = "forwarder_domain"
    login_session_token = "login_session_token"
    tag_key = "tag_key"
