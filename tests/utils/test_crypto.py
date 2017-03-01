import unittest

from unittest.mock import patch, Mock

from spresso.utils.base import create_nonce, get_file_content
from spresso.utils.crypto import encrypt_aes_gcm, decrypt_aes_gcm, \
    create_signature, verify_signature


class CryptoTestCase(unittest.TestCase):
    """
    The OpenSSL module is required for this test to work.
    """

    @patch("spresso.utils.crypto.Cipher")
    @patch("spresso.utils.crypto.algorithms")
    @patch("spresso.utils.crypto.modes")
    @patch("spresso.utils.crypto.default_backend")
    def test_encrypt_aes_gcm(self, backend_mock, modes_mock, algorithms_mock,
                             cipher_mock):
        encryptor_mock = Mock()
        encryptor_mock.update.return_value = "update"
        encryptor_mock.finalize.return_value = "finalize"
        encryptor_mock.tag = "tag"
        cipher = Mock()
        cipher.encryptor.return_value = encryptor_mock
        cipher_mock.return_value = cipher

        algorithm = "aes"
        algorithms_mock.AES.return_value = algorithm

        mode = "gcm"
        modes_mock.GCM.return_value = mode

        backend = "backend"
        backend_mock.return_value = backend

        key = "key"
        iv = "iv"
        plaintext = "text"
        associated_data = "data"

        encrypted = encrypt_aes_gcm(key, iv, plaintext, associated_data)

        algorithms_mock.AES.assert_called_once_with(key)
        modes_mock.GCM.assert_called_once_with(iv)
        self.assertEqual(backend_mock.call_count, 1)

        cipher_mock.assert_called_once_with(algorithm, mode, backend=backend)

        encryptor_mock.authenticate_additional_data.assert_called_once_with(
            associated_data
        )
        encryptor_mock.update.assert_called_once_with(plaintext)
        self.assertEqual(encryptor_mock.finalize.call_count, 1)

        self.assertEqual(encrypted, ("update" + "finalize", "tag"))

    @patch("spresso.utils.crypto.Cipher")
    @patch("spresso.utils.crypto.algorithms")
    @patch("spresso.utils.crypto.modes")
    @patch("spresso.utils.crypto.default_backend")
    def test_decrypt_aes_gcm(self, backend_mock, modes_mock, algorithms_mock,
                             cipher_mock):
        decryptor_mock = Mock()
        decryptor_mock.update.return_value = "update"
        decryptor_mock.finalize.return_value = "finalize"
        decryptor_mock.tag = "tag"
        cipher = Mock()
        cipher.decryptor.return_value = decryptor_mock
        cipher_mock.return_value = cipher

        algorithm = "aes"
        algorithms_mock.AES.return_value = algorithm

        mode = "gcm"
        modes_mock.GCM.return_value = mode

        backend = "backend"
        backend_mock.return_value = backend

        key = "key"
        iv = "iv"
        auth_tag = "tag"
        cipher_text = "cipher"
        associated_data = "data"

        decrypted = decrypt_aes_gcm(key, iv, auth_tag, cipher_text,
                                    associated_data)

        algorithms_mock.AES.assert_called_once_with(key)
        modes_mock.GCM.assert_called_once_with(iv, auth_tag)
        self.assertEqual(backend_mock.call_count, 1)

        cipher_mock.assert_called_once_with(algorithm, mode, backend=backend)

        decryptor_mock.authenticate_additional_data.assert_called_once_with(
            associated_data
        )
        decryptor_mock.update.assert_called_once_with(cipher_text)
        self.assertEqual(decryptor_mock.finalize.call_count, 1)

        self.assertEqual(decrypted, ("update" + "finalize"))

    @patch("spresso.utils.crypto.serialization")
    @patch("spresso.utils.crypto.padding")
    @patch("spresso.utils.crypto.hashes")
    @patch("spresso.utils.crypto.default_backend")
    def test_create_signature(self, backend_mock, hashes_mock, padding_mock,
                              serialization_mock):
        signer_mock = Mock()
        signer_mock.finalize.return_value = "signature"

        private_key_mock = Mock()
        private_key_mock.signer.return_value = signer_mock
        serialization_mock.load_pem_private_key.return_value = private_key_mock

        padding = "pkcs1"
        padding_mock.PKCS1v15.return_value = padding

        hash = "sha256"
        hashes_mock.SHA256.return_value = hash

        backend = "backend"
        backend_mock.return_value = backend

        private_key = "key"
        data = "data"

        signature = create_signature(private_key, data)

        serialization_mock.load_pem_private_key.assert_called_once_with(
            private_key,
            password=None,
            backend=backend
        )

        private_key_mock.signer.assert_called_once_with(
            padding,
            hash
        )
        signer_mock.update.assert_called_once_with(data)
        self.assertEqual(signer_mock.finalize.call_count, 1)
        self.assertEqual(signature, "signature")

    @patch("spresso.utils.crypto.serialization")
    @patch("spresso.utils.crypto.padding")
    @patch("spresso.utils.crypto.hashes")
    @patch("spresso.utils.crypto.default_backend")
    def test_verify_signature(self, backend_mock, hashes_mock, padding_mock,
                              serialization_mock):
        verifier_mock = Mock()

        public_key_mock = Mock()
        public_key_mock.verifier.return_value = verifier_mock
        serialization_mock.load_pem_public_key.return_value = public_key_mock

        padding = "pkcs1"
        padding_mock.PKCS1v15.return_value = padding

        hash = "sha256"
        hashes_mock.SHA256.return_value = hash

        backend = "backend"
        backend_mock.return_value = backend

        public_key = "key"
        signature = "signature"
        data = "data"

        verify_signature(public_key, signature, data)

        serialization_mock.load_pem_public_key.assert_called_once_with(
            public_key,
            backend=backend
        )

        public_key_mock.verifier.assert_called_once_with(
            signature,
            padding,
            hash
        )
        verifier_mock.update.assert_called_once_with(data)
        self.assertEqual(verifier_mock.verify.call_count, 1)

    def test_aes_gcm(self):
        key = create_nonce(32)
        iv = create_nonce(12)
        plaintext = "text"

        enc_text, enc_tag = encrypt_aes_gcm(key, iv, plaintext.encode('utf-8'))

        dec_text = decrypt_aes_gcm(key, iv, enc_tag, enc_text)

        self.assertEqual(dec_text.decode('utf-8'), plaintext)

    def test_signature(self):
        private_key_file = 'test_priv_key.pem'
        public_key_file = 'test_pub_key.pem'

        data = "test".encode('utf-8')
        priv_key = get_file_content(private_key_file, "rb")

        signature = create_signature(priv_key, data)

        pub_key = get_file_content(public_key_file, "rb")

        # This will raise an exception if the signature verification fails
        verify_signature(pub_key, signature, data)
