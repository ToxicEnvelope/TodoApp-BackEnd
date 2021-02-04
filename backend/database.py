from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os.path import dirname, abspath
from platform import platform

isWindows = lambda: platform().lower().startswith('win')

current_dir = dirname(dirname(abspath(__file__)))

db_path_string = f'sqlite:////{current_dir}/todo-task.db' if not isWindows() else r'sqlite:///{0}\todo-tasks.db'.format(current_dir)

engine = create_engine(db_path_string, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def db_init():
    Base.metadata.create_all(bind=engine)
