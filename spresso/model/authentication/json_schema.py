"""
    JSON schema definitions.
"""
from spresso.model.base import JsonSchema


class AuthenticationJsonSchema(JsonSchema):
    """
        Base resource folder.
    """
    resource_path = "resources/authentication/"


class WellKnownInfoDefinition(AuthenticationJsonSchema):
    """
        Well Known Info schema definition.
    """
    file_path = "json/wk_info.json"

    public_key = "public_key"


class IdentityAssertionDefinition(AuthenticationJsonSchema):
    """
        Identity Assertion schmema definition.
    """
    file_path = "json/ia_sig.json"

    ia = "ia_signature"


class StartLoginDefinition(AuthenticationJsonSchema):
    """
        StartLogin schema definition.
    """
    file_path = "json/start_login.json"

    forwarder_domain = "forwarder_domain"
    login_session_token = "login_session_token"
    tag_key = "tag_key"
