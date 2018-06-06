import logging

from flask import Flask
from metadome.domain.services.database_creation import create_db
from metadome.domain.infrastructure import write_all_genes_names_to_disk
from metadome.domain.services.mail.mail import mail
from metadome.domain.services.meta_domain_creation import create_metadomains
from metadome.default_settings import RECONSTRUCT_METADOMAINS

_log = logging.getLogger(__name__)

def create_app(settings=None):
    _log.info("Creating app")

    app = Flask(__name__, static_folder='presentation/web/static',
               template_folder='presentation/web/templates')
    app.config.from_object('metadome.default_settings')
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
    from metadome import _log as metadom_logger
    
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
    

    # Add mail instance
    mail.init_app(app)
 
    # Initialize extensions
    from metadome import toolbar
    toolbar.init_app(app)

    
    # Specify the Blueprints
    from metadome.presentation.web.routes import bp as web_bp
    from metadome.presentation.api.routes import bp as api_bp

    # Register the Blueprints
    app.register_blueprint(api_bp, url_prefix='/metadome/api')
    app.register_blueprint(web_bp, url_prefix='/metadome')
    
    # Database
    from metadome.database import db
    db.init_app(app)
    with app.app_context():
        # Extensions like Flask-SQLAlchemy now know what the "current" app
        # is while within this block. Therefore, you can now run........
        db.create_all()
        create_db()
         
        # now create all meta_domains
        create_metadomains(reconstruct=RECONSTRUCT_METADOMAINS)
         
        # retrieve all gene names and write to disk
        write_all_genes_names_to_disk()
        
    

    return app
