import unittest

from unittest.mock import Mock, patch, call

from spresso.controller.grant.authentication.config.identity_provider import \
    IdentityProvider
from spresso.controller.grant.authentication.config.relying_party import \
    RelyingParty


class SettingsTestCase(unittest.TestCase):
    @patch(
        "spresso.controller.grant.authentication.config.identity_provider."
        "get_file_content")
    def test_identity_provider(self, get_content_mock):
        domain = Mock()
        priv_key_path = Mock()
        pub_key_path = Mock()
        get_content_mock.return_value = "public key"
        idp = IdentityProvider(
            domain,
            priv_key_path,
            pub_key_path
        )

        self.assertEqual(idp.private_key, "public key")
        self.assertEqual(idp.public_key, "public key")

        self.assertEqual(
            get_content_mock.mock_calls[0], call(priv_key_path, "rb")
        )
        self.assertEqual(
            get_content_mock.mock_calls[1], call(pub_key_path, "r")
        )

    @patch.object(RelyingParty, 'fwd_selector')
    @patch("spresso.controller.grant.authentication.config.relying_party."
           "Cache")
    @patch("spresso.controller.grant.authentication.config.relying_party."
           "ForwardDomain")
    def test_relying_party(self, fwd_domain_mock, cache_mock, selection_mock):
        domain = Mock()
        forwarder_domain = Mock()
        fwd_domain_mock.return_value = "domain"
        cache_mock.return_value = "cache"

        rp = RelyingParty(domain, forwarder_domain)
        self.assertEqual(rp.domain, domain)
        fwd_domain_mock.assert_called_once_with("default", forwarder_domain)
        selection_mock.update_default.assert_called_once_with("domain")
        self.assertEqual(rp.scheme_well_known_info, rp.scheme)
        cache_mock.assert_called_once_with(rp)
        self.assertEqual(rp.cache, "cache")
