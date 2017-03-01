from spresso.view.base import TemplateView


class ProxyView(TemplateView):
    def template(self):
        return self.settings.proxy_template
