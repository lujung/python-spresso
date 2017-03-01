from spresso.model.base import Composition
from spresso.view.base import JsonView, SettingsMixin


class SignatureView(JsonView, SettingsMixin):
    def __init__(self, signature, **kwargs):
        super(SignatureView, self).__init__(**kwargs)
        self.signature = signature

    def json(self):
        schema = self.settings.json_schemata.get("sign").schema

        ia_signature = {
            schema.ia: self.signature
        }

        signature = Composition(ia_signature)
        schema.validate(signature)
        signature_json = signature.to_json()
        return signature_json


class WellKnownInfoView(JsonView, SettingsMixin):
    def json(self):
        schema = self.settings.json_schemata.get("info").schema

        wk_info = {
            schema.public_key: self.settings.public_key
        }

        info = Composition(wk_info)
        schema.validate(info)
        info_json = info.to_json()
        return info_json
