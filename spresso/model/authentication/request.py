from spresso.model.base import SettingsMixin
from spresso.model.request import GetRequest


class IdpInfoRequest(SettingsMixin):
    """
        Class to retrieve the well-known information from the IdP.
        Extend this implementation by making requests over the Tor
        network to ensure privacy.
    """

    def __init__(self, netloc, **kwargs):
        super(IdpInfoRequest, self).__init__(**kwargs)
        self.netloc = netloc
        endpoint = self.settings.endpoints_ext.select(netloc)

        self.instance = GetRequest(
            self.settings.scheme_well_known_info,
            netloc,
            endpoint.get("info").path,
            self.settings.verify,
            self.settings.proxies
        )

    def get_content(self):
        """
            Return the Well Known Info from the Identity Provider. Retrieved 
            resources can be cached.
            
            Returns:
                str: The HTTP response content.
        """
        cache = self.settings.cache.get(self.netloc)
        if cache:
            return cache

        response = self.instance.request()

        self.settings.cache.set(
            self.netloc,
            self.settings.caching_settings.select(self.netloc),
            response.text
        )
        return response.text
