from spresso.view.base import TemplateView


class ApiView(TemplateView):
    """View that specifies the template for the api endpoint."""
    def template(self):
        return self.settings.api_template
