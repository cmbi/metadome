from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging

# Create the top-level logger. This is required because Flask's built-in method
# results in loggers with the incorrect level.
_log = logging.getLogger(__name__)

# Declare the base
Base = declarative_base()

# an Engine, which the Session will use for connection
# resources
metadom_engine = create_engine('postgresql://metadom_user:example@metadom_db_1/')
# Base.metadata.create_all(metadom_engine)

# create a configured "Session" class
Session = sessionmaker(bind=metadom_engine)
 
 
#####
# TODO: test if database exists, otherwise create 
# session = Session()
Base.metadata.create_all(metadom_engine)

def list_tables():
    return Base.metadata.tables.keys()

def test_connection():
    try:
        _session = Session()
        metadom_engine.connect()
        _session.commit()
    except OperationalError as e:
        _log.error(e)