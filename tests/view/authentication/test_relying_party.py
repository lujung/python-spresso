import unittest
from base64 import b64encode

from unittest.mock import Mock, patch

from spresso.view.authentication.relying_party import WaitView, RedirectView, \
    StartLoginView, LoginView


class ViewTestCase(unittest.TestCase):
    def test_wait_view(self):
        settings = Mock()
        settings.wait_template = "wait"
        wait_view = WaitView(settings=settings)

        self.assertEqual(wait_view.template(), "wait")

    def test_redirect_view(self):
        settings = Mock()
        settings.redirect_template = "redirect"
        redirect_view = RedirectView(settings=settings)

        self.assertEqual(redirect_view.template(), "redirect")

    @patch("spresso.view.authentication.relying_party.Composition")
    def test_start_login_view(self, composition_mock):
        session = Mock()
        session.token = "token"
        session.tag_key = "key"
        session.forwarder_domain = "fwd"

        model = Mock()
        model.to_json.return_value = "json"
        composition_mock.return_value = model

        schema = Mock()
        schema.forwarder_domain = "fwd"
        schema.login_session_token = "token"
        schema.tag_key = "tag_key"

        schemata = Mock()
        schemata.schema = schema
        settings = Mock()
        settings.json_schemata.get.return_value = schemata

        start_login_view = StartLoginView(
            session,
            settings=settings
        )
        res_json = start_login_view.json()

        call = {
            'fwd': 'fwd',
            'token': b64encode(
                "token".encode('utf-8')
            ).decode('utf-8'),
            'tag_key': b64encode(
                "key".encode('utf-8')
            ).decode('utf-8')
        }

        composition_mock.assert_called_once_with(call)
        self.assertEqual(model.to_json.call_count, 1)
        self.assertEqual(res_json, "json")

    def test_login_view(self):
        login_view = LoginView("test")

        self.assertEqual(login_view.json(), "test")
