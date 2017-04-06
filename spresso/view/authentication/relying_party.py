from spresso.model.base import Composition, SettingsMixin
from spresso.utils.base import to_b64
from spresso.view.base import JsonView, TemplateView


class WaitView(TemplateView):
    """
        View that specifies the template for the wait endpoint.
    """
    def template(self):
        return self.settings.wait_template


class RedirectView(TemplateView):
    """
        View that specifies the template for the redirect endpoint.
    """
    def template(self):
        return self.settings.redirect_template


class StartLoginView(JsonView, SettingsMixin):
    """
        View for the Start Login endpoint.
    """
    def __init__(self, session, **kwargs):
        super(StartLoginView, self).__init__(**kwargs)
        self.session = session

    def json(self):
        """
            Method for returning a validated JSON.

            Returns:
                str: The dumped JSON object, containing the Start Login 
                    information.
        """
        login_session_token = to_b64(self.session.token)
        tag_key = to_b64(self.session.tag_key)

        schema = self.settings.json_schemata.get("start_login").schema

        info_schema = {
            schema.forwarder_domain: self.session.forwarder_domain,
            schema.login_session_token: login_session_token,
            schema.tag_key: tag_key
        }

        info = Composition(info_schema)
        schema.validate(info)
        info_json = info.to_json()
        return info_json


class LoginView(JsonView):
    """
        View for the Login endpoint.
    """
    def __init__(self, user_email):
        super(LoginView, self).__init__()
        self.email = user_email

    def json(self):
        """
            Method for returning the user email.

            Returns:
                str: The email.
        """
        return self.email
