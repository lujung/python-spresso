import unittest

from unittest.mock import Mock, patch

from spresso.view.authentication.identity_provider import SignatureView, \
    WellKnownInfoView


@patch("spresso.view.authentication.identity_provider.Composition")
class ViewTestCase(unittest.TestCase):
    def test_signature_view(self, composition_mock):
        signature = "signature"

        settings = Mock()
        schema = Mock()
        schema.ia = "name"

        model = Mock()
        model.to_json.return_value = "json"
        schemata = Mock()
        schemata.schema = schema
        settings.json_schemata.get.return_value = schemata
        composition_mock.return_value = model

        signature_view = SignatureView(signature, settings=settings)
        res_json = signature_view.json()

        composition_mock.assert_called_once_with({'name': 'signature'})
        self.assertEqual(model.to_json.call_count, 1)
        self.assertEqual(res_json, "json")

    def test_well_known_info_view(self, composition_mock):
        settings = Mock()
        schema = Mock()
        schema.public_key = "name"
        settings.public_key = "public key"
        schemata = Mock()
        schemata.schema = schema
        settings.json_schemata.get.return_value = schemata

        model = Mock()
        model.to_json.return_value = "json"
        composition_mock.return_value = model

        wk_info_view = WellKnownInfoView(settings=settings)
        res_json = wk_info_view.json()

        composition_mock.assert_called_once_with({'name': "public key"})
        self.assertEqual(model.to_json.call_count, 1)
        self.assertEqual(res_json, "json")
