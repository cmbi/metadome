from metadome.factory import create_app, make_celery
# initialize the application and database
app = create_app()

# initialize the celery_application
celery = make_celery(app)
