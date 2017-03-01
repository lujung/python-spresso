import unittest
from urllib.parse import quote

from unittest.mock import Mock, patch, MagicMock

from spresso.controller.grant.authentication.config.relying_party import \
    RelyingParty
from spresso.model.authentication.session import Session
from spresso.model.base import User


class SessionTestCase(unittest.TestCase):
    @patch.object(Session, "_validate_well_known_info")
    @patch.object(Session, "_validate_user")
    @patch.object(Session, "_validate_settings")
    def test_validate(self, settings_mock, user_mock, well_known_mock):
        settings = Mock()
        user = Mock()
        idp_info = Mock()
        session = Session(user, idp_info, settings=settings)

        session.validate()
        self.assertEqual(well_known_mock.call_count, 1)
        self.assertEqual(user_mock.call_count, 1)
        self.assertEqual(settings_mock.call_count, 1)

    def test_validate_user(self):
        settings = Mock()
        user = Mock()
        idp_info = Mock()
        user.is_valid = False

        session = Session(user, idp_info, settings=settings)

        self.assertRaises(
            ValueError,
            session._validate_user
        )

        user = Mock(spec=User)
        user.is_valid = True
        session = Session(user, idp_info, settings=settings)

        session._validate_user()

    @patch("spresso.model.authentication.session.get_url")
    def test_validate_settings(self, get_url_mock):
        settings = Mock()
        user = Mock()
        idp_info = Mock()

        session = Session(user, idp_info, settings=settings)

        self.assertRaises(
            ValueError,
            session._validate_settings
        )

        user.netloc = "netloc"
        settings = Mock(spec=RelyingParty)
        settings.endpoints_ext.select.return_value = "endpoint"
        schema = Mock()
        schema.schema = "schema"
        settings.json_schemata.get.return_value = schema
        settings.scheme = "scheme"
        get_url_mock.return_value = "url"
        fwd = Mock()
        fwd.domain = "fwd"
        fwd.padding = "padding"
        settings.fwd_selector.select.return_value = fwd
        settings.domain = "domain"

        session = Session(user, idp_info, settings=settings)

        session._validate_settings()

        settings.endpoints_ext.select.assert_called_once_with("netloc")
        settings.json_schemata.get.assert_called_once_with("info")
        get_url_mock.assert_called_once_with("scheme", "domain")
        settings.fwd_selector.select.assert_called_once_with("netloc")
        self.assertEqual(session.schema, "schema")
        self.assertEqual(session.rp_origin, "url")
        self.assertEqual(session.padding, "padding")
        self.assertEqual(session.forwarder_domain, "fwd")

    @patch("spresso.model.authentication.session.Composition")
    def test_validate_well_known_info(self, composition_mock):
        settings = Mock()
        user = Mock()
        idp_info = "info"
        composition = MagicMock()
        composition_mock.return_value = composition

        session = Session(user, idp_info, settings=settings)
        schema = Mock()
        schema.public_key = "key"
        session.schema = schema

        session._validate_well_known_info()
        schema.validate.assert_called_once_with(composition)
        self.assertEqual(session.idp_wk, composition)

    @patch("spresso.model.authentication.session.to_b64")
    @patch.object(Session, "_create_tag")
    @patch.object(Session, "_create_ld_path")
    def test_get_login_url(self, ld_path_mock, tag_mock, b64_mock):
        settings = Mock()
        tag = Mock()
        tag_enc = Mock()
        tag_enc_json = "tag_enc"
        tag_enc.to_json.return_value = tag_enc_json
        tag.encrypt.return_value = tag_enc
        tag_mock.return_value = tag
        user = Mock()
        email = "email"
        netloc = Mock()
        user.netloc = netloc
        user.email = email
        idp_info = Mock()
        url = "url"
        ld_path_mock.return_value = url

        session = Session(user, idp_info, settings=settings)
        path = "login"
        session.idp_endpoints = dict(login_path=path)
        protocol = "ftp"
        session.scheme = protocol

        rp_origin = Mock()
        padding = Mock()
        session.rp_origin = rp_origin
        session.padding = padding
        forwarder_domain = "fwd"
        session.forwarder_domain = forwarder_domain

        b64_mock.return_value = session.ia_key

        login_url = session.get_login_url()

        self.assertEqual(tag_mock.call_count, 1)
        tag.encrypt.assert_called_once_with(padding)
        self.assertEqual(ld_path_mock.call_count, 1)
        b64_mock.assert_called_once_with(session.ia_key)
        self.assertEqual(tag_enc.to_json.call_count, 1)
        self.assertEqual(
            login_url,
            "{}#{}&{}&{}&{}".format(
                url,
                quote(tag_enc_json),
                quote(email),
                quote(session.ia_key),
                forwarder_domain
            )
        )

    @patch("spresso.model.authentication.session.Tag")
    def test_create_tag(self, tag_mock):
        settings = Mock()
        tag = Mock()
        tag_mock.return_value = tag
        user = Mock()
        idp_info = Mock()

        session = Session(user, idp_info, settings=settings)
        rp_origin = Mock()
        session.rp_origin = rp_origin

        tag_return = session._create_tag()

        tag_mock.assert_called_once_with(
            rp_origin=rp_origin,
            rp_nonce=session.rp_nonce,
            key=session.tag_key,
            iv=session.tag_iv
        )
        self.assertEqual(tag_return, tag)

    @patch("spresso.model.authentication.session.get_url")
    def test_create_ld_path(self, get_url_mock):
        settings = Mock()
        path = Mock()
        path.path = "path"
        user = Mock()
        netloc = Mock()
        user.netloc = netloc
        idp_info = Mock()
        url = Mock()
        get_url_mock.return_value = url

        session = Session(user, idp_info, settings=settings)
        endpoint = Mock()
        endpoint.get.return_value = path
        session.idp_endpoints = endpoint

        protocol = "ftp"
        session.scheme = protocol

        ld_path = session._create_ld_path()
        get_url_mock.assert_called_once_with(
            protocol,
            netloc,
            "path"
        )
        self.assertEqual(ld_path, url)
