import time

from metadom import _log
from metadom.database import db
from psycopg2 import OperationalError

def list_tables():
    return db.Model.metadata.tables.keys()
  
def test_connection(_db):
    try:
        db.session.commit()
        return True
    except db.OperationalError as e:
        _log.error(e)
    return False
# 
# def initialize_database(app, _db, retry_count=None):
#     if retry_count is None:
#         retry_count = 0
#     
#     if retry_count < app.config['DB_RETRY_CONNECTION_ATTEMPTS']:
#         try:
#             _db.create_all()
#             _db.session.commit()
#         except OperationalError as e:
#             _log.warning(str(e)+"... for "+str(retry_count)+" attempts. Reconnecting...")
#             time.sleep(app.config['DB_RETRY_CONNECTION_TIMEOUT'])
#             initialize_database(retry_count+1)
#     else:
#         _log.error("Could not connect to database after "+str(retry_count)+" attempts.")
