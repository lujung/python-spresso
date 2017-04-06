from spresso.view.base import TemplateView


class ProxyView(TemplateView):
    """
        View that specifies the template for the proxy endpoint.
    """
    def template(self):
        return self.settings.proxy_template
