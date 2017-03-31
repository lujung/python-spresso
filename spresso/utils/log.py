"""
    There is one logger available to log uncaught exceptions in 
    ``spresso.controller.application``.
    If logging has not been configured, you will likely see this error:
    .. code-block:: python
        No handlers could be found for logger "oauth2.application"
    Make sure that logging is configured to avoid this:
    .. code-block:: python
        import logging
        logging.basicConfig()
"""

import logging

app_log = logging.getLogger("spresso.application")
