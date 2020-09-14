from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os.path import dirname, abspath

current_dir = dirname(dirname(abspath(__file__)))

engine = create_engine(f'sqlite:////{current_dir}/todo-tasks.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def db_init():
    Base.metadata.create_all(bind=engine)
