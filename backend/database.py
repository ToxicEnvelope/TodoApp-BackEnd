from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from backend.helpers import PathUtil


db_path_string = PathUtil.get_database_file()
engine = create_engine(db_path_string, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def db_init():
    try:
        Base.metadata.create_all(bind=engine)
    except:
        return False
    return True
