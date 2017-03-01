import unittest
from unittest.mock import Mock, patch

from spresso.controller.grant.authentication.site_adapter.base import \
    IdentityAssertionExtensionSiteAdapter
from spresso.controller.grant.base import SiteAdapterMixin, SettingsMixin, \
    JsonErrorMixin
from spresso.utils.error import InvalidSiteAdapter, InvalidSettings


class SiteAdapter(SiteAdapterMixin):
    site_adapter_class = None


class SettingAdapter(SettingsMixin):
    settings_class = None


class GrantBaseTestCase(unittest.TestCase):
    def test_site_adapter_mixin(self):
        site_adapter = None
        self.assertRaises(
            InvalidSiteAdapter,
            SiteAdapter,
            site_adapter=site_adapter
        )

        SiteAdapter.site_adapter_class = Mock
        self.assertRaises(
            InvalidSiteAdapter,
            SiteAdapter,
            site_adapter=site_adapter
        )

        site_adapter = Mock()
        adapter_class = SiteAdapter(site_adapter=site_adapter)
        self.assertEqual(adapter_class.site_adapter, site_adapter)

    def test_settings_mixin(self):
        settings = None
        self.assertRaises(
            InvalidSettings,
            SettingAdapter,
            settings=settings
        )

        SettingAdapter.settings_class = Mock
        self.assertRaises(
            InvalidSettings,
            SettingAdapter,
            settings=settings
        )

        settings = Mock()
        setting_class = SettingAdapter(settings=settings)
        self.assertEqual(setting_class.settings, settings)

    def test_extended_identity_assertion_site_adapter(self):
        ext_ia_site_adapter = IdentityAssertionExtensionSiteAdapter()
        self.assertEqual(ext_ia_site_adapter.get_additional_data(), {})

    @patch("spresso.controller.grant.base.json_error_response")
    def test_json_error_mixin(self, view_mock):
        grant = JsonErrorMixin()

        error = Mock()
        response = Mock()
        response_value = "response"
        view_mock.return_value = response_value
        res = grant.handle_error(error, response)

        view_mock.assert_called_once_with(error, response)
        self.assertEqual(response_value, res)
