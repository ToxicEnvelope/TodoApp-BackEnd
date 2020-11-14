# TodoApp-BackEnd


This repository contains a test RESTful API Server + SQLite Database managed via SQLAlchmey ORM.

The repository focuses on a `ToDo List` Application backend.

---
#### `How To Use?`
- Backend configuration file:
    - create a config file `backend.json` under the `conf` directory, should contains `{"server_key" : "my-super-secret-server-key"}`
- Install all dependencies via command-line:
    - `pip install -i requirements.txt` or `python -m pip install requirements.txt`
- Simply run `todo_resful_app.py` module by using the command-line:  
    - `python todo_resful_app.py`

---
#### `API's Routes`

The base URI is `/api/v1`
##### `POST: {baseURI}/users/sign-in`
- create a user in the Database , return `status 201`, `status 403`, `status 405` or `status 406`
- payload: `{"name": String, "email": String, "password": String}`
- headers: `JWT` will be produced after a successful `sign-in`

##### `POST: {baseURI}/users/login`
- create a session the Database , return `status 200`, `status 401`, `status 403` or `status 405`
- payload: `{"email": String, "password": String}`
- headers: `JWT` will be produced after a successful `login`

##### `GET: {baseURI}/tasks`  
- get all todo tasks from the Database , return `status 200` or `status 403`

##### `GET: {baseURI}/tasks/<task_id>`  
- get a todo tasks by ID from the Database , return `status 200`, `status 403` or `status 404`

##### `POST: {baseURI}/tasks`  
- create a new todo task in the Database , return `status 201` or `status 403`
- payload: `{"taskDescription": String}`

##### `PUT: {baseURI}/tasks/<task_id>`  
- update a todo task by ID in the Database , return `status 202`, `status 403` or `status 404`
- payload: `{"taskDescription": String, "isCompleted": Boolean}`

##### `DELETE: {baseURI}/tasks/<task_id>`  
- delete a todo task by ID in the Database , return `status 200`, `status 403` or `status 404`

---
#### `Database Schema`

Simple connection to `todo-tasks.db`, no auth required.
We suggest to open the db connection using `DB Browser for SQLite`,
download from here -> https://sqlitebrowser.org/dl

- We have only one Table `todos`.
- The `ToDos` datatype module located at package `modules/datatypes.py` represented by `SQLAlchemy` as an ORM,
We suggest to check the `SQLAlchemy` API Docs for more information from here -> https://docs.sqlalchemy.org/en/13/index.html

