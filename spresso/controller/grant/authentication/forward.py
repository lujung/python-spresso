from spresso.controller.grant.base import GrantHandler
from spresso.model.base import SettingsMixin
from spresso.view.authentication.forward import ProxyView
from spresso.view.base import Script


class ProxyHandler(GrantHandler, SettingsMixin):
    def process(self, request, response, environ):
        script = Script(settings=self.settings)

        view = ProxyView(settings=self.settings)
        view.template_context = dict(script=script.render())

        return view.process(response)
