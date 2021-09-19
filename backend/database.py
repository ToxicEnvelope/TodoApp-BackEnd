from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os.path import dirname, abspath, join
from platform import platform

def path_resolver():
    if platform().lower().startswith('win'):
        final_dir = r'%s' % join(dirname(dirname(abspath(__file__))))
        relative_path = r'sqlite:///%s\todo-app.db' % final_dir
    else:
        final_dir = '%s' % join(dirname(dirname(abspath(__file__))))
        relative_path = 'sqlite:////%s/todo-app.db' % final_dir

    final_path = relative_path
    return final_path

db_path_string = path_resolver()

engine = create_engine(db_path_string, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def db_init():
    Base.metadata.create_all(bind=engine)
