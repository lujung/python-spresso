from spresso.utils.error import InvalidSiteAdapter, InvalidSettings
from spresso.view.base import json_error_response


class ErrorHandler(object):
    def handle_error(self, error, response):
        raise NotImplementedError


class GrantHandler(object):
    def process(self, request, response, environ):
        raise NotImplementedError


class ValidatingGrantHandler(GrantHandler, ErrorHandler):
    def read_validate_params(self, request):
        raise NotImplementedError


class GrantHandlerFactory(object):
    def __call__(self, request, application):
        raise NotImplementedError


class SiteAdapterMixin(object):
    site_adapter_class = None

    def __init__(self, site_adapter, **kwargs):
        if self.site_adapter_class is None:
            raise InvalidSiteAdapter("Undefined 'site_adapter_class'")

        if not isinstance(site_adapter, self.site_adapter_class):
            raise InvalidSiteAdapter(
                "Site adapter must inherit from class '{0}'".format(
                    self.site_adapter_class.__name__
                )
            )

        self.site_adapter = site_adapter
        super(SiteAdapterMixin, self).__init__(**kwargs)


class SettingsMixin(object):
    settings_class = None

    def __init__(self, settings, **kwargs):
        if self.settings_class is None:
            raise InvalidSettings("Undefined 'settings_class'")

        if not isinstance(settings, self.settings_class):
            raise InvalidSettings(
                "Setting class must inherit from class '{0}'".format(
                    self.settings_class.__name__
                )
            )

        self.settings = settings
        super(SettingsMixin, self).__init__(**kwargs)


class JsonErrorMixin(ErrorHandler):
    def handle_error(self, error, response):
        return json_error_response(error, response)
