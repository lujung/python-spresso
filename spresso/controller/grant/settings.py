import warnings

from spresso.model.settings import Container


class Setting(object):
    _available_schemes = ["http", "https"]
    endpoints = Container()
    scheme = "https"
    debug = False

    def __setattr__(self, key, value):
        if key == "scheme":
            if value not in self._available_schemes:
                raise ValueError(
                    "'scheme' must be one of '{}'".format(
                        self._available_schemes
                    )
                )
            if value == "http":
                warnings.warn(
                    "\nThe SPRESSO system is running on HTTP, this setting "
                    "renders the system insecure!\nThis should only be used in "
                    "development environments.\nIf you are running a production"
                    " environment, make sure all traffic is transferred over "
                    "HTTPS!",
                    RuntimeWarning
                )
        super(Setting, self).__setattr__(key, value)
