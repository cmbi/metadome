import logging
from flask_debugtoolbar import DebugToolbarExtension

_VERSION = '1.0.0 - alpha'

# for using the Flask debug toolbar throughout the application
toolbar = DebugToolbarExtension()

# Create the top-level logger. This is required because Flask's built-in method
# results in loggers with the incorrect level.
_log = logging.getLogger(__name__)

def get_version():
    return _VERSION