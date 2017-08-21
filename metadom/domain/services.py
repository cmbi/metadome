from metadom import _log
from metadom.database import db

def list_tables():
    return db.Model.metadata.tables.keys()
  
def test_connection():
    try:
        db.session.commit()
        return True
    except db.OperationalError as e:
        _log.error(e)
    return False