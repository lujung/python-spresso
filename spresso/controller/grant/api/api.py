from spresso.controller.grant.base import GrantHandler
from spresso.view.api.api import ApiView


class ApiInformationHandler(GrantHandler):
    def __init__(self, application, settings, **kwargs):
        super(ApiInformationHandler, self).__init__(**kwargs)
        self.application = application
        self.settings = settings

    def process(self, request, response, environ):
        context = dict(grants=self.application.grant_types)
        view = ApiView(settings=self.settings)
        view.template_context = context
        return view.process(response)
