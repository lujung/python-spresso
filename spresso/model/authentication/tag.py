from spresso.model.base import Composition
from spresso.utils.base import to_b64, create_random_characters, \
    update_existing_keys
from spresso.utils.crypto import encrypt_aes_gcm


class TagBase(Composition):
    max_domain_length = 256

    template = Composition(
        rp_nonce=None,
        rp_origin=None
    )

    def __init__(self, rp_origin, rp_nonce, key, iv, **kwargs):
        super(TagBase, self).__init__(**kwargs)
        self.tag = Composition()
        self.tag.update(self.template)
        self.rp_origin = rp_origin
        self.rp_nonce = rp_nonce
        self.key = key
        self.iv = iv


class Tag(TagBase):
    def encrypt(self, padding=True):
        if None in [self.rp_nonce, self.rp_origin]:
            raise ValueError("Empty required parameter in tag")

        self.rp_nonce = to_b64(self.rp_nonce)

        if padding:
            # Prevent Tag length side channel attacks by padding
            padding_length = self.max_domain_length - len(self.rp_origin)
            self.rp_origin += "={0}".format(
                create_random_characters(padding_length - 1)
            )

        # Create Tag
        update_existing_keys(self, self.tag)

        if None in [*self.tag, self.key, self.iv]:
            raise ValueError("Empty required parameter during encryption")

        tag_json = self.tag.to_json().encode('utf-8')

        # Encrypt
        cipher_text, auth_tag = encrypt_aes_gcm(self.key, self.iv, tag_json)

        iv = to_b64(self.iv)
        encrypted_tag = to_b64(cipher_text + auth_tag)
        return Composition(iv=iv, ciphertext=encrypted_tag)
