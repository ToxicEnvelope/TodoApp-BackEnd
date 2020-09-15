# TodoApp-BackEnd


This repository contains a test RESTful API Server + SQLite Database managed via SQLAlchmey ORM.

The repository focuses on a `ToDo List` Application backend.

---
#### `How To Use?`

- Before all, make sure to `pip install requirements.txt` to install all dependencies.
- Simply run `todo_resful_app.py` module by using the command-line:  
        - `python todo_resful_app.py`
        
---
#### `API's Routes`

The base URI is `/api/v1`
##### `GET: {baseURI}/todos`  

- get all todo tasks from the Database , return `status 200` or `status 403`
##### `GET: {baseURI}/todos/<task_id>`  

- get a todo tasks by ID from the Database , return `status 200`, `status 403` or `status 404`
##### `POST: {baseURI}/todos`  

- create a new todo task in the Database , return `status 201` or `status 403`
- payload: `{"taskDescription": String}`
##### `PUT: {baseURI}/todos/<task_id>`  

- update a todo task by ID in the Database , return `status 202`, `status 403` or `status 404`
- payload: `{"taskDescription": String, "isCompleted": Boolean}`
##### `DELETE: {baseURI}/todos/<task_id>`  

- delete a todo task by ID in the Database , return `status 200`, `status 403` or `status 404`

---
#### `Database Schema`

Simple connection to `todo-tasks.db`, no auth required.
We suggest to open the db connection using `DB Browser for SQLite`,
download from here -> https://sqlitebrowser.org/dl

- We have only one Table `todos`.
- The `ToDos` datatype module located at package `modules/datatypes.py` represented by `SQLAlchemy` as an ORM,
We suggest to check the `SQLAlchemy` API Docs for more information from here -> https://docs.sqlalchemy.org/en/13/index.html

