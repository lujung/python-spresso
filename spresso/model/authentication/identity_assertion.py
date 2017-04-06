from spresso.model.base import Composition, SettingsMixin
from spresso.utils.base import update_existing_keys, to_b64, from_b64
from spresso.utils.crypto import create_signature, decrypt_aes_gcm, \
    verify_signature
from spresso.utils.error import InvalidSettings


class IdentityAssertionBase(Composition, SettingsMixin):
    """
        Basic Identity Assertion Class.
        The template instances 'signature' and 'expected_signature'
        can be extended to hold further information.
        Object is used by IdP and RP.
    """
    template = Composition(
        tag=None,
        email=None,
        forwarder_domain=None
    )

    def __init__(self, **kwargs):
        super(IdentityAssertionBase, self).__init__(**kwargs)
        self.expected_signature = Composition()
        self.expected_signature.update(self.template)
        self.signature = Composition()
        self.signature.update(self.template)
        self.tag = None
        self.email = None
        self.forwarder_domain = None
        self.public_key = None
        self.iv = None
        self.cipher_text = None
        self.ia_key = None

    def from_session(self, session):
        """
            Load an Identity Assertion from a :class:`Session` object.
            
            Args:
                session(:class:`Session`): The session instance.
        """
        self.tag = session.tag_enc_json
        self.email = session.user.email
        self.forwarder_domain = session.forwarder_domain
        self.ia_key = session.ia_key
        self.public_key = session.idp_wk.public_key

    def from_request(self, request):
        """
            Load an Identity Assertion from a request object.
            
            Args:
                request(:class:`Request`): The request instance.
        """
        self.email = request.post_param('email')
        self.tag = request.post_param('tag')
        self.forwarder_domain = request.post_param('forwarder_domain')


class IdentityAssertion(IdentityAssertionBase):
    def sign(self):
        """
            Method for signing the identity assertion.
            
            Returns:
                str: The b64-encoded signature.
            
            Raises:
                ValueError: Attempt of creating a signature from a malformed IA.
                InvalidSettings: The private key is missing.
        """
        # Update IA template with values from self
        update_existing_keys(self, self.signature)

        if self.settings.private_key is None:
            raise InvalidSettings(
                "Private key is empty"
            )

        if None in self.signature.values():
            raise ValueError(
                "Empty required parameter during signature creation"
            )

        # Create b64 encoded JSON
        ia_json = self.signature.to_json()
        ia_json_bytes = ia_json.encode('utf-8')

        # Create signature
        signature = create_signature(self.settings.private_key, ia_json_bytes)
        return to_b64(signature)

    def decrypt(self, data):
        """
            Decrypt the encrypted Identity Assertion.
            
            Args:
                data(str): The encrypted IA as serialized JSON.
            
            Returns:
                bytes: The decrypted IA as serialized JSON.
            
            Raises:
                ValueError: A required parameter of the encrypted IA is missing.
        
        """
        eia = Composition()
        eia.from_json(data)

        self.iv = eia.iv
        self.cipher_text = eia.ciphertext

        if None in [self.iv, self.cipher_text, self.ia_key]:
            raise ValueError(
                "Empty required parameter in encrypted Identity Assertion"
            )

        self.iv = from_b64(self.iv, return_bytes=True)
        self.cipher_text = from_b64(self.cipher_text, return_bytes=True)

        # First 12 characters for iv
        iv = self.iv[:12]

        # Last 16 characters for authentication tag
        auth_tag = self.cipher_text[-16:]

        # Remaining characters for cipher text
        cipher_text = self.cipher_text[0:-16]

        # Decrypt tag, in this case no additional authentication data is used
        return decrypt_aes_gcm(self.ia_key, iv, auth_tag, cipher_text)

    def verify(self, signature):
        """
            Verifies with a public key from whom the data came that it was 
            indeed signed by their private key.
            
            Args:
                signature(bytes): The Identity Assertion as serialized JSON.
            
            Raises:
                ValueError: A required parameter to perform the verification 
                is missing.
                InvalidSignature: The signature verification of the IA failed.
        """
        # Get signature from IA
        if signature is None:
            raise ValueError("Empty required parameter during: signature")

        ia = signature.decode('utf-8')

        ia_json = Composition()
        ia_json.from_json(ia)

        signature_b64 = ia_json.ia_signature
        signature_bytes = from_b64(signature_b64, return_bytes=True)

        # Update IA template with values from self
        update_existing_keys(self, self.expected_signature)

        if None in [*self.expected_signature.values(), self.public_key]:
            raise ValueError("Empty required parameter in expected signature")

        # Get expected signature
        expected_signature = self.expected_signature.to_json()
        expected_signature_bytes = expected_signature.encode('utf-8')
        public_key_bytes = self.public_key.encode('utf-8')

        # Verify, throws exception on failure
        verify_signature(
            public_key_bytes,
            signature_bytes,
            expected_signature_bytes
        )
