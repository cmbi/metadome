from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Declare the base
Base = declarative_base()

# an Engine, which the Session will use for connection
# resources
# TODO: connect to db container @metadom_db_1
metadom_engine = create_engine('postgresql://metadom_user:example@metadom_db_1/')
# Base.metadata.create_all(metadom_engine)

# create a configured "Session" class
Session = sessionmaker(bind=metadom_engine)


#####
# TODO: test if database exists, otherwise create 
# session = Session()
Base.metadata.create_all(metadom_engine)

# session.commit()
