import jwt
from functools import wraps
from flask import Flask, jsonify, request, session, make_response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db_session, db_init
from time import time
from modules.datatypes import Todos, Users, datetime, __COMPLETED__, __NOT_STARTED__
from backend import Config

app = Flask(__name__)
CORS(app)


app.config['SECRET_KEY'] = Config.get('server_key')

__BASE_URI = '/api/v1'
__STATUS_SUCCESS = 'success'
__STATUS_FAIL = 'fail'
__STATUS_TEST = 'test'
__STATUS_NOT_FOUND = 'not found'

stamp = lambda: int(time().__str__()[:10])


def get_jwt_decode_data():
    token = request.headers.get('Authorization')
    session_data = jwt.decode(token, app.config['SECRET_KEY'])
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
            data = jwt.decode(token, app.config['SECRET_KEY'])
            print(data)
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


@app.route(rule=f'{__BASE_URI}/status', methods=['GET'])
def status():
    response = {
        'timestamp': stamp(),
        'status': __STATUS_TEST
    }
    resp = make_response(response)
    resp.status_code = 200
    return resp


@app.route(rule=f'{__BASE_URI}/heartbeat', methods=['GET'])
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
        "status": __STATUS_SUCCESS,
        "timestamp": stamp()
    }
    resp = make_response(response)
    resp.status_code = 200
    return resp


@app.route(rule=f'{__BASE_URI}/users/sign-in', methods=['POST'])
def create_new_user():
    '''
        :description:
            - user sign in , creation of new user
        :generate:
            - new user object in todo-tasks db
        :param:
            - accepts JSON with
                'name', 'email', 'password'
        :returns:
            - JSON response
    '''
    recall = request
    if recall.method.__eq__('POST'):
        data = recall.get_json()
        if data is None or data["email"] is None or data["password"] is None:
            e = Exception('data is missing!')
            response = {
                "status": STATUS_FAILED,
                "timestamp": stamp(),
                "reason": e.__str__()
            }
            resp = make_response(response)
            resp.status_code = 403
            return resp
        user_name = data['name']
        user_email = data['email']
        hashed_password = generate_password_hash(data['password'], method='sha256')
        optional_user = Users.query.filter_by(email=user_email).first()
        if optional_user is None:
            new_user = Users(user_name, user_email, hashed_password)
            new_user.token = new_user.encode_auth_token(new_user.id)
            db_session.add(new_user)
            db_session.commit()
            session['logged_in'] = True
            response = {
                "status": __STATUS_SUCCESS,
                "timestamp": stamp()
            }
            resp = make_response(response)
            resp.headers['Authorization'] = new_user.token.decode()
            resp.status_code = 201
            return resp
        else:
            e = Exception("User already exists!")
            response = {
                "status": __STATUS_FAIL,
                "timestamp": stamp(),
                "reason": e.__str__()
            }
            resp = make_response(response)
            resp.status_code = 406
            return resp
    e = Exception("Unable to process request!")
    response = {
        "status": __STATUS_FAIL,
        "timestamp": stamp(),
        "reason": e.__str__()
    }
    resp = make_response(response)
    resp.status_code = 405
    return resp


@app.route(rule=f'{__BASE_URI}/users/login', methods=['POST'])
def user_login():
    '''
        :description:
            - make a login with existing user
        :param:
            - accepts JSON with
                'email', 'password'
        :return:
            - JSON response
    '''
    recall = request
    if recall.method.__eq__('POST'):
        data = recall.get_json()
        if data is None or len(data) == 0:
            e = Exception('data is missing!')
            response = {
                "status": __STATUS_FAIL,
                "timestamp": stamp(),
                "reason": e.__str__()
            }
            resp = make_response(response)
            resp.status_code = 403
            return resp
        user_email = data['email']
        user_password = data['password']
        optional_user = Users.query.filter_by(email=user_email).first()
        if optional_user is not None and check_password_hash(optional_user.password, user_password):
            session['logged_in'] = True
            auth_token = optional_user.encode_auth_token(optional_user.id)
            optional_user.token = auth_token
            assert optional_user.token == auth_token
            db_session.add(optional_user)
            db_session.commit()
            response = {
                "status": __STATUS_SUCCESS,
                "timestamp": stamp(),
                "message": "Login Successfully!",
            }
            resp = make_response(response)
            resp.headers['Authorization'] = optional_user.token.decode()
            resp.status_code = 200
            return resp
        else:
            e = Exception("Unauthorized! email / password is not correct.")
            response = {
                "status": __STATUS_FAIL,
                "timestamp": stamp(),
                "reason": e.__str__()
            }
            resp = make_response(response)
            resp.status_code = 401
            return resp
    e = Exception("Unable to verify WWW-Authenticate: Basic realm 'login realm'")
    response = {
        "status": __STATUS_FAIL,
        "timestamp": stamp(),
        "reason": e.__str__()
    }
    resp = make_response(response)
    resp.status_code = 405
    return resp


@app.route(rule=f'{__BASE_URI}/tasks', methods=['GET'])
@check_for_token
def get_all_todo_task():
    '''
        :description:
            - retrieve all tasks associated to user by token from todo-tasks db
        :return:
            - JSON response
    '''
    if request.method == 'GET':
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if optional_user is None:
            response = {
                "status": __STATUS_FAIL,
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
            'status': __STATUS_SUCCESS,
            'data': content
        }
        resp = make_response(response)
        resp.status_code = 200
        return resp
    response = {
        'timestamp': stamp(),
        'status': __STATUS_FAIL
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp


@app.route(rule=f'{__BASE_URI}/tasks/<task_id>', methods=['GET'])
@check_for_token
def get_todo_task_by_id(task_id):
    '''
        :description:
            - retrieve a single task object from todo-tasks db
        :param:
            - URL params
                'task_id'
        :return:
            - JSON response
    '''
    if request.method == 'GET':
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if optional_user is None:
            response = {
                "status": __STATUS_FAIL,
                "timestamp": stamp()
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        todo_obj = Todos.query.filter_by(user_id=optional_user.id, id=task_id).first()
        if todo_obj is None:
            response = {
                'timestamp': stamp(),
                'status': __STATUS_NOT_FOUND,
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
            'status': __STATUS_SUCCESS,
            'data': todo_obj_data
        }
        resp = make_response(response)
        resp.status_code = 200
        return resp
    response = {
        'timestamp': stamp(),
        'status': __STATUS_FAIL
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp


@app.route(rule=f'{__BASE_URI}/tasks', methods=['POST'])
@check_for_token
def add_new_todo_task():
    '''
        :description:
            - create a new task associated with user by token
        :param:
            - accepts JSON with
                'taskDescription'
        :return:
            - JSON response
    '''
    if request.method == 'POST':
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if optional_user is None:
            response = {
                "status": __STATUS_FAIL,
                "timestamp": stamp()
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        payload = request.get_json()
        task_description = payload['taskDescription']
        new_todo = Todos(user_id=optional_user.id, todo_description=task_description)
        db_session.add(new_todo)
        db_session.commit()
        response = {
            'timestamp': stamp(),
            'status': __STATUS_SUCCESS,
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
        'status': __STATUS_FAIL
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp


@app.route(rule=f'{__BASE_URI}/tasks/<task_id>', methods=['PUT'])
@check_for_token
def update_todo_task_by_id(task_id):
    '''
        :description:
            - update an existing task resource to todo-tasks db
        :param:
            - URL params
                'task_id'
        :return:
            - JSON response
    '''
    if request.method == 'PUT':
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if optional_user is None:
            response = {
                "status": __STATUS_FAIL,
                "timestamp": stamp()
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        todo_obj = Todos.query.filter_by(user_id=optional_user.id, id=task_id).first()
        if todo_obj is None:
            response = {
                'timestamp': stamp(),
                'status': __STATUS_NOT_FOUND,
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
            'status': __STATUS_SUCCESS,
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
        'status': __STATUS_FAIL
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp


@app.route(rule=f'{__BASE_URI}/tasks/<task_id>', methods=['DELETE'])
@check_for_token
def delete_todo_task_by_id(task_id):
    '''
        :description:
            - delete an existing task resource associated to user by token from todo-tasks db
        :param:
            - URL param
                'task_id'
        :return:
            - JSON response
    '''
    if request.method == 'DELETE':
        session_data = get_jwt_decode_data()
        optional_user = Users.query.filter_by(id=session_data['sub']).first()
        if optional_user is None:
            response = {
                "status": __STATUS_FAIL,
                "timestamp": stamp()
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        todo_obj = Todos.query.filter_by(user_id=optional_user.id, id=task_id).first()
        if todo_obj is None:
            response = {
                'timestamp': stamp(),
                'status': __STATUS_NOT_FOUND,
                'data': {}
            }
            resp = make_response(response)
            resp.status_code = 404
            return resp
        db_session.delete(todo_obj)
        db_session.commit()
        response = {
            'timestamp': stamp(),
            'status': __STATUS_SUCCESS
        }
        resp = make_response(response)
        resp.status_code = 200
        return resp
    response = {
        'timestamp': stamp(),
        'status': __STATUS_FAIL
    }
    resp = make_response(response)
    resp.status_code = 403
    return resp


if __name__ == '__main__':
    import sys
    # if '--debug' in sys.argv:
    #     app.run('0.0.0.0', 8081, debug=True)
    # else:
    #     app.run('0.0.0.0', 8081, debug=False)
    app.run('0.0.0.0', 8081, debug=True)
