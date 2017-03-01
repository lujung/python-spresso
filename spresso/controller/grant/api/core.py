from spresso.controller.grant.api.api import ApiInformationHandler
from spresso.controller.grant.api.settings import ApiInformationSettings
from spresso.controller.grant.base import GrantHandlerFactory, SettingsMixin


class ApiInformation(GrantHandlerFactory, SettingsMixin):
    settings_class = ApiInformationSettings

    def __call__(self, request, application):
        if request.path == self.settings.endpoints.get('api_info').path and \
           request.method in self.settings.endpoints.get('api_info').methods:
            return ApiInformationHandler(application, self.settings)
