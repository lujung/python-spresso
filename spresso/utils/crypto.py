"""This module provides the necessary cryptographic primitives for the system.
It is based on the `cryptography <https://cryptography.io/en/latest/>`_
package."""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def encrypt_aes_gcm(key, iv, plaintext, associated_data=b""):
    """
    Method for encrypting AES-GCM
    :param key: byte
    :param plaintext: byte
    :param associated_data: byte
    :param iv: byte
    :return: byte, byte
    """

    #: Construct an AES-GCM Cipher object with the given key and a
    #: randomly generated IV.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    #: Associated_data will be authenticated but not encrypted,
    #: it must also be passed in on decryption.
    encryptor.authenticate_additional_data(associated_data)

    #: Encrypt the plaintext and get the associated cipher text.
    #: GCM does not require padding.
    cipher_text = encryptor.update(plaintext) + encryptor.finalize()

    return cipher_text, encryptor.tag


def decrypt_aes_gcm(key, iv, auth_tag, cipher_text, associated_data=b""):
    """Method to decrypt AES in GCM mode.

    Constructs a :class:`Cipher <cryptography.hazmat.primitives.ciphers.Cipher>`
    object from key, iv and authentication tag. The associated data is passed in
    during decryption.

    Args:
        key (bytes): The symmetric key used during decryption.
        iv (bytes): The initialisation vector used during decryption.
        auth_tag (bytes): The authentication tag used during decryption.
        cipher_text (bytes): Cipher text to decrypt.
        associated_data (bytes): Additional authentication data that was passed
            in during encryption.

    Returns:
        bytes: The decrypted cipher text as bytes.

    Raises:
        InvalidTag: The authentication tag in combination with the given
            parameters is invalid.
    """
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, auth_tag),
        backend=default_backend()
    ).decryptor()

    decryptor.authenticate_additional_data(associated_data)
    plaintext = decryptor.update(cipher_text) + decryptor.finalize()
    return plaintext


def create_signature(private_key, data):
    """
    Create PKCS#1 signature using SHA256.
    :param private_key: byte
    :param data: byte
    :return: byte
    """

    private_key = serialization.load_pem_private_key(
        private_key,
        password=None,
        backend=default_backend()
    )

    signer = private_key.signer(
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    signer.update(data)
    signed_data = signer.finalize()
    return signed_data


def verify_signature(public_key, signature, data):
    """
    Verify PKCS#1 signature using SHA256.
    Raises an InvalidSignature Exception on failure.
    :param public_key: byte
    :param signature: byte
    :param data: byte
    :return:
    """

    public_key = serialization.load_pem_public_key(
        public_key,
        backend=default_backend()
    )

    verifier = public_key.verifier(
        signature,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    verifier.update(data)
    verifier.verify()
