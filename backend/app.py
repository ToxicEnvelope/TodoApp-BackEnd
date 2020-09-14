from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.database import db_session, db_init
from time import time
from modules import Todos, datetime, __COMPLETED__, __NOT_STARTED__

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'wA-hKPtOY3HDrBU_PFiLeBE6CeNJ8j3cSMd14VAf11v7LVvxyatmHKKsylWSTNar0sr1VJNxoXYG9GwB-HaZcQ'

__BASE_URI = '/api/v1'
__STATUS_SUCCESS = 'success'
__STATUS_FAIL = 'fail'
__STATUS_TEST = 'test'
__STATUS_NOT_FOUND = 'not found'

stamp = lambda: int(time().__str__()[:10])



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
    return jsonify(response), 200


@app.route(rule=f'{__BASE_URI}/tasks', methods=['GET'])
def get_all_todo_task():
    if request.method == 'GET':
        all_todos = Todos.query.filter_by(is_completed=False).all()
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
        return jsonify(response), 200
    response = {
        'timestamp': stamp(),
        'status': __STATUS_FAIL
    }
    return jsonify(response), 403


@app.route(rule=f'{__BASE_URI}/tasks/<task_id>', methods=['GET'])
def get_todo_task_by_id(task_id):
    if request.method == 'GET':
        todo_obj = Todos.query.filter_by(id=task_id).first()
        if todo_obj is None:
            response = {
                'timestamp': stamp(),
                'status': __STATUS_NOT_FOUND,
                'data': {}
            }
            return jsonify(response), 404
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
        return jsonify(response), 200
    response = {
        'timestamp': stamp(),
        'status': __STATUS_FAIL
    }
    return jsonify(response), 403


@app.route(rule=f'{__BASE_URI}/tasks', methods=['POST'])
def add_new_todo_task():
    if request.method == 'POST':
        payload = request.get_json()
        task_description = payload['taskDescription']
        new_todo = Todos(todo_description=task_description)
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
        return jsonify(response), 201
    response = {
        'timestamp': stamp(),
        'status': __STATUS_FAIL
    }
    return jsonify(response), 403


@app.route(rule=f'{__BASE_URI}/tasks/<task_id>', methods=['PUT'])
def update_todo_task_by_id(task_id):
    if request.method == 'PUT':
        todo_obj = Todos.query.filter_by(id=task_id).first()
        if todo_obj is None:
            response = {
                'timestamp': stamp(),
                'status': __STATUS_NOT_FOUND,
                'data': {}
            }
            return jsonify(response), 404
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
        return jsonify(response), 202
    response = {
        'timestamp': stamp(),
        'status': __STATUS_FAIL
    }
    return jsonify(response), 403


@app.route(rule=f'{__BASE_URI}/tasks/<task_id>', methods=['DELETE'])
def delete_todo_task_by_id(task_id):
    if request.method == 'DELETE':
        todo_obj = Todos.query.filter_by(id=task_id).first()
        if todo_obj is None:
            response = {
                'timestamp': stamp(),
                'status': __STATUS_NOT_FOUND,
                'data': {}
            }
            return jsonify(response), 404
        db_session.delete(todo_obj)
        db_session.commit()
        response = {
            'timestamp': stamp(),
            'status': __STATUS_SUCCESS
        }
        return jsonify(response), 200
    response = {
        'timestamp': stamp(),
        'status': __STATUS_FAIL
    }
    return jsonify(response), 403

