import sys
import jwt
import logging
from functools import wraps
from flask.logging import create_logger
from flask import Flask, request, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db_session, db_init, db_path_string
from backend.helpers import PathUtil
from modules.datatypes import Todos, Users, datetime, __COMPLETED__, __NOT_STARTED__

app = Flask(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    filemode='w',
    filename=PathUtil.get_logs_path(),
    format='%(threadName)s_%(thread)d | %(filename)s | %(asctime)s | %(levelname)s | %(message)s'
)
create_logger(app)
sys.stdout.write('\n [+] Database Location Path : %s\n' % PathUtil.get_database_path())
sys.stdout.write(' [+] Logs Runtime Path : %s\n\n' % PathUtil.get_logs_path())
sys.stdout.write(' -----------------------------------------------------\n\n')

app.config['SECRET_KEY'] = 'd032c84b34cdb5b061af09151a758688bc732371'
Success = 'success'
Fail = 'fail'


def stamp():
    return datetime.datetime.now().isoformat()


def get_jwt_decode_data():
    token = request.headers.get('Authorization')
    session_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    return session_data


def check_for_token(func, header='Authorization'):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.headers.get(header)
        if not token:
            session['logged_in'] = False
            resp = make_response({'message': 'Missing token'})
            resp.status_code = 403
            return resp
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            assert 'sub' in data
            
        except:
            session['logged_in'] = False
            resp = make_response({'message': 'Invalid token'})
            resp.status_code = 403
            return resp
        return func(*args, **kwargs)
    return wrapped


@app.before_first_request
def database_init():
    db_init()


@app.teardown_appcontext
def session_shutdown(exception=None):
    db_session.remove()


@app.route(rule='/api/heartbeat', methods=['GET'])
@check_for_token
def heartbeat():
    data = get_jwt_decode_data()
    exp = data["exp"]
    now = datetime.datetime.utcnow() - datetime.timedelta(days=0, seconds=600)
    now = int(now.timestamp().__str__()[:10])
    state = exp - now
    if state <= 0:
        session['log_in'] = False
        resp = make_response({'message': 'Invalid token'})
        resp.status_code = 403
        return resp
    user_obj = Users.query.filter_by(id=data["sub"]).first()
    new_token = user_obj.encode_auth_token(user_obj.id)
    user_obj.token = new_token
    db_session.add(user_obj)
    db_session.commit()
    response = {
        "status": Success,
        "timestamp": stamp()
    }
    resp = make_response(response)
    resp.status_code = 200
    return resp


@app.route(rule='/api/users/register', methods=['POST'])
def user_register():
    if request.method.__eq__('POST'):
        data = request.get_json()
        if not data or not data["email"] or not data["password"]:
            response = {
                "status": Fail,
                "timestamp": stamp(),
                "reason": "data is missing!"
            }
            resp = make_response(response)
            resp.status_code = 403
            return resp
        user_name = data['name']
        user_email = data['email']
        hashed_password = generate_password_hash(data['password'], method='sha256')
        optional_user = Users.query.filter_by(email=user_email).first()
        if not optional_user:
            new_user = Users(user_name, user_email, hashed_password)
            new_user.token = new_user.encode_auth_token(new_user.id)
            db_session.add(new_user)
            db_session.commit()
            session['logged_in'] = True
            response = {
                "status": Success,
                "timestamp": stamp()
            }
            resp = make_response(response)
            resp.headers['Authorization'] = new_user.token
            resp.status_code = 201
            return resp
        else:
            response = {
                "status": Fail,
                "timestamp": stamp(),
                "reason": "user already exists!"
            }
            resp = make_response(response)
            resp.status_code = 406
            return resp
    response = {
        "status": Fail,
        "timestamp": stamp(),
        "reason": "unable to process request!"
    }
    resp = make_response(response)
    resp.status_code = 405
    return resp


@app.route(rule='/api/users/login', methods=['POST'])
def user_login():
    if request.method.__eq__('POST'):
        data = request.get_json()
        if not data or len(data) == 0:
            response = {
                "status": Fail,
                "timestamp": stamp(),
                "reason": "data is missing!"
            }
            resp = make_response(response)
            resp.status_code = 403
            return resp
        user_email = data['email']
        user_password = data['password']
        optional_user = Users.query.filter_by(email=user_email).first()
        if optional_user and check_password_hash(optional_user.password, user_password):
            session['logged_in'] = True
            auth_token = optional_user.encode_auth_token(optional_user.id)
            optional_user.token = auth_token
            assert optional_user.token == auth_token
            db_session.add(optional_user)
            db_session.commit()
            response = {
                "status": Success,
                "timestamp": stamp()
            }
            resp = make_response(response)
            resp.headers['Authorization'] = optional_user.token
            resp.status_code = 200
            return resp
        else:
            response = {
                "status": Fail,
                "timestamp": stamp(),
                "reason": "unauthorized! email / password is not correct"
            }
            resp = make_response(response)
            resp.status_code = 401
            return resp
    response = {
        "status": Fail,
        "timestamp": stamp(),
        "reason": "Unable to verify WWW-Authenticate: Basic realm 'login realm'"
    }
    resp = make_response(response)
    resp.status_code = 405
    return resp


@app.route(rule='/api/tasks', methods=['GET'])
@check_for_token
def get_all_todo_task():
    if request.method.__eq__('GET'):
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if not optional_user:
            response = {
                "status": Fail,
                "timestamp": stamp()
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        all_todos = Todos.query.filter_by(user_id=optional_user.id, is_completed=False).all()
        content = []
        for todo_obj in all_todos:
            todo_obj_data = {
                'taskId': todo_obj.id,
                'taskDescription': todo_obj.task_description,
                'taskCreationTime': todo_obj.time_created,
                'taskCompletionStatus': todo_obj.task_status
            }
            content.append(todo_obj_data)
        response = {
            'timestamp': stamp(),
            'status': Success,
            'data': content
        }
        resp = make_response(response)
        resp.status_code = 200
        return resp
    response = {
        'timestamp': stamp(),
        'status': Fail
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp


@app.route(rule='/api/tasks/<task_id>', methods=['GET'])
@check_for_token
def get_todo_task_by_id(task_id):
    if request.method.__eq__('GET'):
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if not optional_user:
            response = {
                "status": Fail,
                "timestamp": stamp(),
                "reason": "no such user"
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        todo_obj = Todos.query.filter_by(user_id=optional_user.id, id=task_id).first()
        if not todo_obj:
            response = {
                'timestamp': stamp(),
                'status': Fail,
                'data': {}
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        todo_obj_data = {
            'taskId': todo_obj.id,
            'taskDescription': todo_obj.task_description,
            'taskCreationTime': todo_obj.time_created,
            'taskCompletionStatus': todo_obj.task_status
        }
        response = {
            'timestamp': stamp(),
            'status': Success,
            'data': todo_obj_data
        }
        resp = make_response(response)
        resp.status_code = 200
        return resp
    response = {
        'timestamp': stamp(),
        'status': Fail
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp


@app.route(rule='/api/tasks', methods=['POST'])
@check_for_token
def add_new_todo_task():
    if request.method.__eq__('POST'):
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if not optional_user:
            response = {
                "status": Fail,
                "timestamp": stamp(),
                "reason": "no such user"
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        payload = request.get_json()
        task_description = payload['taskDescription']
        new_todo = Todos(user_id=optional_user.id)
        new_todo.task_description = task_description
        db_session.add(new_todo)
        db_session.commit()
        response = {
            'timestamp': stamp(),
            'status': Success,
            'data': {
                'taskId': new_todo.id,
                'taskCreationTime': new_todo.time_created
            }
        }
        resp = make_response(response)
        resp.status_code = 201
        return resp
    response = {
        'timestamp': stamp(),
        'status': Fail
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp


@app.route(rule='/api/tasks/<task_id>', methods=['PUT'])
@check_for_token
def update_todo_task_by_id(task_id):
    if request.method.__eq__('PUT'):
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if not optional_user:
            response = {
                "status": Fail,
                "timestamp": stamp(),
                "reason": "no such user"
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        todo_obj = Todos.query.filter_by(user_id=optional_user.id, id=task_id).first()
        if not todo_obj:
            response = {
                'timestamp': stamp(),
                'status': Fail,
                'data': {}
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        payload = request.get_json()
        task_description = payload['taskDescription']
        task_status = payload['isCompleted']
        if task_status:
            todo_obj.task_status = __COMPLETED__
            todo_obj.is_completed = True
        else:
            todo_obj.task_status = __NOT_STARTED__
            todo_obj.is_completed = False
        todo_obj.task_description = task_description
        todo_obj.time_created = datetime.datetime.now()
        db_session.commit()
        response = {
            'timestamp': stamp(),
            'status': Success,
            'data': {
                'taskId': todo_obj.id,
                'taskUpdateTime': todo_obj.time_created
            }
        }
        resp = make_response(response)
        resp.status_code = 202
        return resp
    response = {
        'timestamp': stamp(),
        'status': Fail
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp


@app.route(rule='/api/tasks/<task_id>', methods=['DELETE'])
@check_for_token
def delete_todo_task_by_id(task_id):
    if request.method.__eq__('DELETE'):
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if not optional_user:
            response = {
                "status": Fail,
                "timestamp": stamp(),
                "reason": "no such user"
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        todo_obj = Todos.query.filter_by(user_id=optional_user.id, id=task_id).first()
        if not todo_obj:
            response = {
                'timestamp': stamp(),
                'status': Fail,
                'data': {}
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        db_session.delete(todo_obj)
        db_session.commit()
        response = {
            'timestamp': stamp(),
            'status': Success
        }
        resp = make_response(response)
        resp.status_code = 200
        return resp
    response = {
        'timestamp': stamp(),
        'status': Fail
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp
