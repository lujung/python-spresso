import json
import unittest
from base64 import b64encode, b64decode

from unittest.mock import patch, MagicMock

from spresso.model.authentication.tag import Tag, TagBase
from spresso.model.base import Composition
from spresso.utils.base import create_nonce
from spresso.utils.crypto import decrypt_aes_gcm


class TagBaseTestCase(unittest.TestCase):
    def test_init(self):
        tag_base = TagBase("", "", "", "")

        for key in tag_base.template:
            self.assertIn(key, tag_base.tag)


class TagTestCase(unittest.TestCase):
    @patch("spresso.model.authentication.tag.update_existing_keys")
    @patch("spresso.model.authentication.tag.Composition")
    @patch("spresso.model.authentication.tag.to_b64")
    @patch("spresso.model.authentication.tag.create_random_characters")
    @patch("spresso.model.authentication.tag.encrypt_aes_gcm")
    def test_encrypt(self, encrypt_mock, random_char_mock, b64_mock,
                     composition_mock, update_mock):
        rp_nonce = "nonce"
        rp_origin = "origin"
        key = "key"
        iv = "iv"

        tag = Tag(rp_origin, rp_nonce, key, iv)
        _tag = MagicMock(spec=Composition)
        _tag.rp_nonce = "nonce"
        _tag.rp_origin = "origin"
        _tag.to_json.return_value = "tag json"
        tag.tag = _tag

        b64_mock.return_value = "b64"
        random_char_mock.return_value = "random_choice"
        encrypt_mock.return_value = ("cipher", "tag")
        composition_mock.return_value = "return"

        tag_return = tag.encrypt()

        self.assertEqual(b64_mock.call_count, 3)
        random_char_mock.assert_called_once_with((256 - len("origin")) - 1)
        update_mock.assert_called_once_with(tag, tag.tag)
        encrypt_mock.assert_called_once_with(
            "key",
            "iv",
            "tag json".encode('utf-8')
        )
        composition_mock.assert_called_with(iv="b64", ciphertext="b64")
        self.assertEqual(tag_return, "return")

    def test_encrypt_functional(self):
        # Parameter
        rp_nonce = None
        rp_origin = "origin"
        key = create_nonce(32)
        iv = create_nonce(12)
        tag = Tag(rp_origin, rp_nonce, key, iv)

        self.assertRaises(ValueError, tag.encrypt, padding=False)

        tag.rp_nonce = "nonce"

        # Functionality without padding
        tag_enc = tag.encrypt(padding=False)
        iv = b64decode(tag_enc.iv)
        auth_tag = b64decode(tag_enc.ciphertext)[-16:]
        cipher_text = b64decode(tag_enc.ciphertext)[0:-16]

        plaintext = decrypt_aes_gcm(
            key=tag.key,
            iv=iv,
            auth_tag=auth_tag,
            cipher_text=cipher_text
        )
        plaintext = json.loads(plaintext.decode('utf-8'))

        self.assertEqual(plaintext["rp_origin"], "origin")
        self.assertEqual(
            plaintext["rp_nonce"],
            b64encode("nonce".encode('utf-8')).decode('utf-8')
        )

        tag = Tag(rp_origin, rp_nonce, key, iv)

        # Functionality with padding
        tag.rp_nonce = "nonce"
        tag.rp_origin = "origin"
        tag.key = create_nonce(32)
        tag.iv = create_nonce(12)
        tag_enc = tag.encrypt(padding=True)
        iv = b64decode(tag_enc.iv)
        auth_tag = b64decode(tag_enc.ciphertext)[-16:]
        cipher_text = b64decode(tag_enc.ciphertext)[0:-16]

        plaintext = decrypt_aes_gcm(
            key=tag.key,
            iv=iv,
            auth_tag=auth_tag,
            cipher_text=cipher_text
        )
        plaintext = json.loads(plaintext.decode('utf-8'))

        self.assertEqual(plaintext["rp_origin"].split("=")[0], "origin")
        self.assertEqual(
            plaintext["rp_nonce"],
            b64encode("nonce".encode('utf-8')).decode('utf-8')
        )
