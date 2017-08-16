from metadom.factory import create_app, create_blueprints
# initialize the application and database
app, db = create_app()

# initialize the user interface
create_blueprints(app)