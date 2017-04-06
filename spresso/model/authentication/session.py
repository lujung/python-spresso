from urllib.parse import quote

from spresso.controller.grant.authentication.config.relying_party import \
    RelyingParty
from spresso.model.authentication.tag import Tag
from spresso.model.base import Composition, SettingsMixin, User
from spresso.utils.base import create_nonce, get_url, to_b64


class Session(SettingsMixin):
    """
        Session object, used by the Relying Party. Validates input parameters.
        Processes the Tag and generates the login URL.
    """
    def __init__(self, user, idp_info, **kwargs):
        super(Session, self).__init__(**kwargs)
        self.user = user
        self.idp_info = idp_info
        self.rp_nonce = create_nonce(32)
        self.token = create_nonce(32)
        self.ia_key = create_nonce(32)
        self.tag_key = create_nonce(32)
        self.tag_iv = create_nonce(12)

    def validate(self):
        """
            Validate the user, the settings and the Well Known info.
        """
        self._validate_user()
        self._validate_settings()
        self._validate_well_known_info()

    def _validate_user(self):
        if not isinstance(self.user, User) or not self.user.is_valid:
            raise ValueError(
                "'user' must be of type {0}".format(User.__name__)
            )

    def _validate_settings(self):
        if not isinstance(self.settings, RelyingParty):
            raise ValueError(
                "'config' must be of type {0}".format(
                    RelyingParty.__name__
                )
            )

        self.idp_endpoints = self.settings.endpoints_ext.select(
            self.user.netloc
        )
        self.schema = self.settings.json_schemata.get("info").schema
        self.scheme = self.settings.scheme
        self.rp_origin = get_url(
            self.settings.scheme,
            self.settings.domain
        )
        forward = self.settings.fwd_selector.select(self.user.netloc)
        self.padding = forward.padding
        self.forwarder_domain = forward.domain

    def _validate_well_known_info(self):
        request_json = Composition()
        request_json.from_json(self.idp_info)

        self.schema.validate(request_json)

        idp_wk = Composition(
            public_key=request_json[self.schema.public_key]
        )
        self.idp_wk = idp_wk

    def get_login_url(self):
        """
            Create, encrypt and serialize the Tag. Generate a Login 
            URL using all information necessary for the login flow.
        
            Returns:
                str: The login URL.
        """
        tag = self._create_tag()
        tag_enc = tag.encrypt(self.padding)
        ld_path = self._create_ld_path()

        self.tag_enc_json = tag_enc.to_json()
        email = self.user.email
        ia_key = to_b64(self.ia_key)

        login_url = "{}#{}&{}&{}&{}".format(
            ld_path,
            quote(self.tag_enc_json),
            quote(email),
            quote(ia_key),
            self.forwarder_domain
        )
        return login_url

    def _create_tag(self):
        tag = Tag(
            rp_origin=self.rp_origin,
            rp_nonce=self.rp_nonce,
            key=self.tag_key,
            iv=self.tag_iv
        )
        return tag

    def _create_ld_path(self):
        email_netloc = self.user.netloc

        ld_path = get_url(
            self.scheme,
            email_netloc,
            self.idp_endpoints.get("login").path
        )
        return ld_path
