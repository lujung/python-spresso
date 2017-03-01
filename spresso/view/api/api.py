from spresso.view.base import TemplateView


class ApiView(TemplateView):
    def template(self):
        return self.settings.api_template
