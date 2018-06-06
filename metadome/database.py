from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_schemadisplay import create_schema_graph

db = SQLAlchemy()

## Save the schema of the database
def write_db_schema_graph(schema_filename):
    # create the pydot graph object by autoloading all tables via a bound metadata object
    graph = create_schema_graph(metadata=db.Model.metadata,
       show_datatypes=True, # The image would get nasty big if we'd show the datatypes
       show_indexes=True, # ditto for indexes
       rankdir='LR', # From left to right (instead of top to bottom)
       concentrate=False # Don't try to join the relation lines together
    )
    graph.write_png(schema_filename) # write out the file