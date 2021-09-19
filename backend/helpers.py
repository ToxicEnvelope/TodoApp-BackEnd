import datetime
import sys
from platform import platform
from os.path import join, dirname, abspath

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class PathUtil(object, metaclass=Singleton):
    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
        else:
            base_path = join(dirname(abspath(__file__)), '..')
        return join(base_path, relative_path)

    @staticmethod
    def get_database_path():
        if platform().lower().startswith('win'):
            final_path = PathUtil.resource_path('todo-app.db')
            database_path = r'sqlite:///%s' % final_path
        else:
            final_path = PathUtil.resource_path('todo-app.db')
            database_path = 'sqlite:////%s' % final_path
        return database_path

    @staticmethod
    def get_logs_path():
        if platform().lower().startswith('win'):
            final_path = PathUtil.resource_path(r'runtime_%s.log' % datetime.date.today())
            logs_dir = r'%s' % final_path
        else:
            final_path = PathUtil.resource_path('runtime_%s.log' % datetime.date.today())
            logs_dir = '%s' % final_path
        return logs_dir
