import logging
from metadom.database import db

_log = logging.getLogger(__name__)

def list_tables():
    return db.Model.metadata.tables.keys()
  
def test_connection():
    try:
        db.session.commit()
        return True
    except db.OperationalError as e:
        _log.error(e)
    return False

def fill_db():
    pass