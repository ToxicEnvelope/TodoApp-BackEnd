from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os.path import dirname, abspath, join
from platform import platform
import sys

global name


def path_resolver():
    global name
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
    else:
        base_path = join(dirname(abspath(__file__)), '..')
    if platform().lower().startswith('win'):
        final_dir = r'%s_%s' % (base_path, name)
        relative_path = r'sqlite:///%s\todo-app.db' % final_dir
    else:
        final_dir = '%s_%s' % (base_path, name)
        relative_path = 'sqlite:////%s/todo-app.db' % final_dir

    final_path = join(final_dir, relative_path)
    sys.stdout.write(' [+] Database Location Path : %s' % final_path)
    return final_path

db_path_string = path_resolver()
"""db_path_string = f'sqlite:////{current_dir}/todo-task.db' if not isWindows() else r'sqlite:///{0}\todo-tasks.db'.format(current_dir)"""

engine = create_engine(db_path_string, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def db_init():
    Base.metadata.create_all(bind=engine)
