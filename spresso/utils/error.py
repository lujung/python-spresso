class InvalidSiteAdapter(Exception):
    """
        Raised by :class:`spresso.grant.base.SiteAdapterMixin` in case an 
        invalid site adapter was passed to the instance.
    """
    pass


class InvalidSettings(Exception):
    """
        Raised by :class:`spresso.grant.base.SettingsMixin` in case an 
        invalid settings class was passed to the instance.
    """
    pass


class SpressoBaseError(Exception):
    """
        Base class used by SPRESSO specific errors.
        
        Args:
            error (str): Identifier of the error.
            uri (str): URL at which the error occurred.
            message (str): Short message that describes the error.
    """

    def __init__(self, error, uri=None, message=None):
        self.error = error
        self.uri = uri
        self.explanation = message

        super(SpressoBaseError, self).__init__()


class SpressoInvalidError(SpressoBaseError):
    """
        Indicates an error during validation of a request.
    """
    pass


class UserNotAuthenticated(Exception):
    """
        Raised by :class:`spresso.grant.authentication.site_adapter.
        identity_provider.SignatureSiteAdapter` to indicate an unauthenticated
        user.
    """
    pass


class UnsupportedGrantError(Exception):
    """
        Indicates that a requested grant is not supported by the server.
    """
    pass


class UnsupportedAdditionalData(Exception):
    """
        Indicates incorrectly formatted additional data.
    """
    pass
