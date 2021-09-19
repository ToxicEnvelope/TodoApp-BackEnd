from os.path import dirname, abspath, join, exists, expanduser
from platform import platform
from os import mkdir
from time import time
from datetime import datetime
from hashlib import sha1
import logging
import sys


def stamp(): return time()
def now(): return datetime.now().isoformat()
def response_hex_id(): return sha1(time().hex().encode('utf-7')).hexdigest()
def validate(data=None, validation=None):
    if validation is 'register':
        state = any(True for key in ['firstName', 'lastName', 'email', 'password'] if key not in data.keys())
    elif validation is 'login':
        state = any(True for key in ['email', 'password'] if key not in data.keys())
    elif validation is 'task-create':
        state = any(True for key in ['taskDescription'] if key not in data.keys())
    elif validation is 'task-update':
        state = any(True for key in ['taskDescription', 'isCompleted'] if key not in data.keys())
    elif validation is 'task-remove':
        state = any(True for key in ['taskID'] if key not in data.keys())
    else:
        state = False
    return state

class Singleton(type):
    """ Simple Singleton implementation """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PathUtil(object, metaclass=Singleton):
    """ PathUtil object responsible to handle, retrieve and manage PathLike requests """
    @staticmethod
    def __get_directory(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
        else:
            base_path = join(dirname(abspath(__file__)), '..')
        return join(base_path, relative_path)

    @staticmethod
    def get_logs_dir():
        """ Get absolute path of logs directory """
        if not exists(PathUtil.__get_directory('logs')):
            mkdir(PathUtil.__get_directory('logs'))
        return PathUtil.__get_directory('logs')

    @staticmethod
    def get_database_file():
        if platform().lower().startswith('win'):
            database_path = r'sqlite:///%s\todo-app.db' % expanduser('~/Desktop')
        else:
            database_path = 'sqlite:////%s/todo-app.db' % expanduser('~/Desktop')
        return database_path

class Logger:
    def __init__(self, logger_ref=None):
        logging.basicConfig(
            filemode='w',
            filename='%s/runtime.log' % PathUtil.get_logs_dir(),
            format='%(threadName)s_%(thread)d | %(filename)s | %(asctime)s | %(levelname)s  | %(message)s',
            level=logging.DEBUG
        )
        self.__log = logging.getLogger('app') if not logger_ref else logger_ref

    def info(self, msg):
        self.__log.info(msg)

    def warn(self, msg):
        self.__log.warn(msg)

    def critical(self, msg):
        self.__log.critical(msg)

    def error(self, msg):
        self.__log.error(msg)
