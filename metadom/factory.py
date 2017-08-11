import logging

from flask import Flask

_log = logging.getLogger(__name__)


def create_app(settings=None):
    _log.info("Creating app")

    app = Flask(__name__)
    app.config.from_object('metadom.default_settings')
    if settings:
        app.config.update(settings)

    # Ignore Flask's built-in logging
    # app.logger is accessed here so Flask tries to create it
    app.logger_name = "nowhere"
    app.logger

    # Configure logging.
    #
    # It is somewhat dubious to get _log from the root package, but I can't see
    # a better way. Having the email handler configured at the root means all
    # child loggers inherit it.
    from metadom import _log as metadom_logger

    # Only log to the console during development and production, but not during
    # testing.
    if app.testing:
        metadom_logger.setLevel(logging.DEBUG)
    else:
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        metadom_logger.addHandler(ch)

        if app.debug:
            metadom_logger.setLevel(logging.DEBUG)
        else:
            metadom_logger.setLevel(logging.INFO)

    # Blueprints
    from metadom.presentation.web.routes import bp as web_bp
    from metadom.presentation.api.routes import bp as api_bp
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    return app