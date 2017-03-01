class InvalidSiteAdapter(Exception):
    pass


class InvalidSettings(Exception):
    pass


class SpressoBaseError(Exception):
    def __init__(self, error, uri=None, message=None):
        self.error = error
        self.uri = uri
        self.explanation = message

        super(SpressoBaseError, self).__init__()


class SpressoInvalidError(SpressoBaseError):
    pass


class UserNotAuthenticated(Exception):
    pass


class UnsupportedGrantError(Exception):
    pass


class UnsupportedAdditionalData(Exception):
    pass
