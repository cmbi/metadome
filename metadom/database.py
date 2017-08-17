from metadom.application import db
from metadom import _log

from sqlalchemy.exc import OperationalError

def list_tables():
    return db.Model.metadata.tables.keys()
 
def test_connection():
    try:
        db.session.commit()
        return True
    except OperationalError as e:
        _log.error(e)
    return False