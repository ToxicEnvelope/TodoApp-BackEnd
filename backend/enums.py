from enum import Enum

__BASE_API__ = '/api'
class AppRoutes(Enum):
    Users = '%s/users' % __BASE_API__
    Login = '%s/users/login' % __BASE_API__
    Register = '%s/users/register' % __BASE_API__
    Tasks = '%s/tasks' % __BASE_API__
    TaskById = '%s/tasks/<task_id>' % __BASE_API__
    Health = '%s/health' % __BASE_API__


class AppStates(Enum):
    Success = 'success'
    Fail = 'fail'
    Pending = 'pending'
