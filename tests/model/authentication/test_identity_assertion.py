import json
import unittest
from base64 import b64encode

from unittest.mock import Mock, patch, MagicMock

from spresso.model.authentication.identity_assertion import \
    IdentityAssertionBase, IdentityAssertion
from spresso.model.base import Composition
from spresso.model.web.wsgi import WsgiRequest
from spresso.utils.base import create_nonce, get_file_content
from spresso.utils.crypto import encrypt_aes_gcm
from spresso.utils.error import InvalidSettings


class IdentityAssertionBaseTestCase(unittest.TestCase):
    def test_init(self):
        settings = Mock()
        ia_base = IdentityAssertionBase(settings=settings)

        for key in ia_base.template:
            for member in [ia_base.signature, ia_base.expected_signature]:
                self.assertIn(key, member)

    def test_from_session(self):
        session = Mock()
        tag = "tag"
        session.tag_enc_json = tag
        email = "email"
        session.user.email = email
        forwarder_domain = "fwd"
        session.forwarder_domain = forwarder_domain
        ia_key = "key"
        session.ia_key = ia_key
        public_key = "public key"
        session.idp_wk.public_key = public_key
        settings = Mock()
        ia = IdentityAssertionBase(settings=settings)
        ia.from_session(session)

        self.assertEqual(ia.tag, tag)
        self.assertEqual(ia.email, email)
        self.assertEqual(ia.forwarder_domain, forwarder_domain)
        self.assertEqual(ia.ia_key, ia_key)
        self.assertEqual(ia.public_key, public_key)

    def test_from_request(self):
        content_length = "42"
        request_method = "POST"
        query_string = ""
        email = "email"
        tag = "tag"
        fwd = "fwd"
        content = "email={}&tag={}&forwarder_domain={}".format(
            email,
            tag,
            fwd
        )

        wsgi_input_mock = Mock(spec=["read"])
        wsgi_input_mock.read.return_value = content.encode('utf-8')

        origin_header = "origin"
        environment = {
            "CONTENT_LENGTH": content_length,
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "REQUEST_METHOD": request_method,
            "QUERY_STRING": query_string,
            "HTTP_ORIGIN": origin_header,
            "PATH_INFO": "/",
            "wsgi.input": wsgi_input_mock
        }

        request = WsgiRequest(environment)

        settings = Mock()
        ia = IdentityAssertionBase(settings=settings)
        ia.from_request(request)

        self.assertEqual(ia.email, email)
        self.assertEqual(ia.tag, tag)
        self.assertEqual(ia.forwarder_domain, fwd)


class IdentityAssertionTestCase(unittest.TestCase):
    def setUp(self):
        self.private_key_file = 'test_priv_key.pem'
        self.public_key_file = 'test_pub_key.pem'
        self.tag = "tag"
        self.email = "test@test.com"
        self.fwd = "fwd.test"
        settings = Mock()
        settings.private_key = open(self.private_key_file, mode='rb').read()

        ia = IdentityAssertion(settings=settings)
        ia.tag = self.tag
        ia.email = self.email
        ia.forwarder_domain = self.fwd
        ia.current_file = __file__
        self.signature = ia.sign()

    @patch(
        "spresso.model.authentication.identity_assertion.update_existing_keys")
    @patch("spresso.model.authentication.identity_assertion.create_signature")
    @patch("spresso.model.authentication.identity_assertion.to_b64")
    def test_sign(self, b64_mock, create_signature_mock, update_mock):
        settings = Mock()
        settings.private_key = "key"

        create_signature_mock.return_value = "signature"
        b64_mock.return_value = "signature_b64"

        ia = IdentityAssertion(settings=settings)
        ia.signature.tag = "tag"
        ia.signature.email = "email"
        ia.signature.forwarder_domain = "fwd"

        signature = ia.sign()

        update_mock.assert_called_once_with(ia, ia.signature)
        create_signature_mock.assert_called_once_with(
            "key",
            json.dumps(
                dict(
                    tag="tag",
                    email="email",
                    forwarder_domain="fwd"
                ),
                sort_keys=True
            ).encode('utf-8')
        )
        b64_mock.assert_called_once_with("signature")
        self.assertEqual(signature, "signature_b64")

    def test_sign_error(self):
        # Parameter
        settings = Mock()
        settings.private_key = None
        ia = IdentityAssertion(settings=settings)

        self.assertRaises(InvalidSettings, ia.sign)

        ia.tag = self.tag
        ia.email = self.email
        ia.forwarder_domain = self.fwd
        settings.private_key = "key"
        ia = IdentityAssertion(settings=settings)

        self.assertRaises(ValueError, ia.sign)

    @patch("spresso.model.authentication.identity_assertion.Composition")
    @patch("spresso.model.authentication.identity_assertion.from_b64")
    @patch("spresso.model.authentication.identity_assertion.decrypt_aes_gcm")
    def test_decrypt(self, decrypt_mock, b64_mock, composition_mock):
        eia = Mock()
        eia.iv = "iv"
        eia.ciphertext = "cipher"
        composition_mock.return_value = eia
        b64_mock.return_value = "0123456789" * 10

        settings = Mock()
        settings.private_key = None
        ia = IdentityAssertion(settings=settings)
        ia.ia_key = "key"

        data = "data"

        ia.decrypt(data)

        self.assertEqual(composition_mock.call_count, 3)
        eia.from_json.assert_called_once_with(data)
        self.assertEqual(b64_mock.call_count, 2)
        decrypt_mock.assert_called_once_with(
            "key",
            ("0123456789" * 10)[:12],
            ("0123456789" * 10)[-16:],
            ("0123456789" * 10)[0:-16]
        )

    def test_decrypt_functional(self):
        # Parameter
        settings = Mock()
        settings.private_key_path = self.private_key_file
        ia = IdentityAssertion(settings=settings)

        self.assertRaises(ValueError, ia.decrypt, "")

        # Functionality
        key = create_nonce(32)
        iv = create_nonce(12)
        signature = self.signature.encode('utf-8')
        signature_encrypted, auth_tag = encrypt_aes_gcm(
            key=key,
            iv=iv,
            plaintext=signature
        )
        ia.ia_key = key
        iv = b64encode(iv).decode('utf-8')
        cipher_text = b64encode(signature_encrypted + auth_tag).decode('utf-8')
        eia_json = json.dumps(dict(iv=iv, ciphertext=cipher_text))
        signature_decrypted = ia.decrypt(eia_json)

        self.assertEqual(signature, signature_decrypted)

    @patch("spresso.model.authentication.identity_assertion.Composition")
    @patch("spresso.model.authentication.identity_assertion.from_b64")
    @patch(
        "spresso.model.authentication.identity_assertion.update_existing_keys")
    @patch("spresso.model.authentication.identity_assertion.verify_signature")
    def test_verify(self, verify_mock, update_mock, b64_mock, composition_mock):
        settings = Mock()
        ia = IdentityAssertion(settings=settings)
        expected_signature = MagicMock(spec=Composition)
        expected_signature.tag = "tag"
        expected_signature.email = "email"
        expected_signature.forwarder_domain = "fwd"
        expected_signature.to_json.return_value = "expected signature"

        ia.expected_signature = expected_signature
        ia.public_key = "key"

        ia_json = Mock()
        ia_json.ia_signature = "signature b64"
        composition_mock.return_value = ia_json

        b64_mock.return_value = "signature bytes"

        signature = "signature".encode('utf-8')

        ia.verify(signature)

        self.assertEqual(composition_mock.call_count, 3)
        ia_json.from_json.assert_called_once_with("signature")
        b64_mock.assert_called_once_with("signature b64", return_bytes=True)
        update_mock.assert_called_once_with(ia, ia.expected_signature)
        verify_mock.assert_called_once_with(
            "key".encode('utf-8'),
            "signature bytes",
            "expected signature".encode('utf-8')
        )

    def test_verify_functional(self):
        # Parameter
        settings = Mock()
        settings.private_key_path = self.private_key_file
        ia = IdentityAssertion(settings=settings)

        self.assertRaises(ValueError, ia.verify, None)

        signature = b'{"ia_signature": "test"}'

        self.assertRaises(ValueError, ia.verify, signature)

        # Functionality
        signature = json.dumps({"ia_signature": self.signature}).encode('utf-8')
        ia.public_key = get_file_content(self.public_key_file, "r")
        ia.tag = self.tag
        ia.email = self.email
        ia.forwarder_domain = self.fwd
        ia.verify(signature)
