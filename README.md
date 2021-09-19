# TodoApp-BackEnd


This repository contains a test RESTful API Server + SQLite Database managed via SQLAlchmey ORM.

The repository focuses on a `ToDo List` Application backend.

---
## `How To Use?`
1. Install all dependencies via command-line:
```shell
$ pip install -r ./requirements.txt
```
2. Simply run `todo_resful_app.py` module by using the command-line:
```shell
$ python ./todo_resful_app.py
```

---
## `API's Routes`
#### Register API
- register new user
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<route>
  <url>
    /api/users/register
  </url>
  <method>
    POST
  </method>
  <description>
    register a user
  </description>
  <request using="json">
    json={"name": "my name", "email": "my-email@company.com", "password": "my-password"}
  </request>
  <response>
    <on-success code="201">
      data={"status": "success", "timestamp": "2021-09-19T22:33:20.844168"}, headers={"authorization": "token"}
    </on-success>
    <on-failure code="403">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "data is missing!"}
    </on-failure>
    <on-failure code="406">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "user already exists!"}
    </on-failure>
    <on-failure code="405">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "unable to process request!"}
    </on-failure>
  </response>
</route>
```
---

#### Login API
- authenticate with an existing user
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<route>
  <url>
    /api/users/login
  </url>
  <method>
    POST
  </method>
  <description>
    authenticate a user
  </description>
  <request using="json">
    json={"email": "my-email@company.com", "password": "my-password"}
  </request>
  <response>
    <on-success code="200">
      data={"status": "success", "timestamp": "2021-09-19T22:33:20.844168"}, headers={"authorization": "token"}
    </on-success>
    <on-failure code="403">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "data is missing!"}
    </on-failure>
    <on-failure code="401">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "unauthorized! email / password is not correct"}
    </on-failure>
    <on-failure code="405">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "unable to verify WWW-Authenticate: Basic realm 'login realm'"}
    </on-failure>
  </response>
</route>
```
---

#### Get All Tasks API
- retrieve all tasks 
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<route>
  <url>
    /api/tasks
  </url>
  <method>
    GET
  </method>
  <description>
    get all tasks associated with current logged in user
  </description>
  <request using="header">
    header={"authorization": "token"}
  </request>
  <response>
    <on-success code="200">
      data={"status": "success", "timestamp": "2021-09-19T22:33:20.844168", "data": [{"taskId": 1234, "taskDescription": "description",  "taskCreationTime": "2021-09-19T22:33:20.844168", "taskCompletionStatus": "COMPLETED" / "NOT STARTED"}]}, headers={"authorization": "token"}
    </on-success>
    <on-failure code="404">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168"}
    </on-failure>
    <on-failure code="403">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168"}
    </on-failure>
  </response>
</route>
```
---

#### Get Task by ID API
- retrieve a single todo task with task id
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<route>
  <url>
    /api/tasks/1234-5678-9012-3456
  </url>
  <method>
    GET
  </method>
  <description>
    get a single associated task current logged in user by id
  </description>
  <request using="header">
    header={"authorization": "token"}
  </request>
  <response>
    <on-success code="200">
      data={"status": "success", "timestamp": "2021-09-19T22:33:20.844168", "data": {"taskId": 1234, "taskDescription": "description",  "taskCreationTime": "2021-09-19T22:33:20.844168", "taskCompletionStatus": "COMPLETED" / "NOT STARTED"}}, headers={"authorization": "token"}
    </on-success>
    <on-failure code="404">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "data": {}}
    </on-failure>
    <on-failure code="404">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "no such user"}
    </on-failure>
    <on-failure code="403">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168"}
    </on-failure>
  </response>
</route>
```
---

#### Task Create API
- create a todo task
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<route>
  <url>
    /api/tasks
  </url>
  <method>
    POST
  </method>
  <description>
    get all tasks associated with current logged in user
  </description>
  <request using="json+header">
    json={"taskDescription": "description"}, header={"authorization": "token"}
  </request>
  <response>
    <on-success code="201">
      data={"status": "success", "timestamp": "2021-09-19T22:33:20.844168", "data": {"taskId": 1234, "taskCreationTime": "2021-09-19T22:33:20.844168"}, headers={"authorization": "token"}
    </on-success>
    <on-failure code="404">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "no such user"}
    </on-failure>
    <on-failure code="403">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168"}
    </on-failure>
  </response>
</route>
```
---

#### Task Update API
- update a todo task
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<route>
  <url>
    /api/tasks/1234-5678-9012-3456
  </url>
  <method>
    PUT
  </method>
  <description>
    update a single todo task by id which associated to a current logged in user
  </description>
  <request using="json+header">
    json={"taskDescription": "description", "isCompleted": true or false}, header={"authorization": "token"}
  </request>
  <response>
    <on-success code="202">
      data={"status": "success", "timestamp": "2021-09-19T22:33:20.844168", "data": {"taskId": 1234, "taskCreationTime": "2021-09-19T22:33:20.844168"}, headers={"authorization": "token"}
    </on-success>
    <on-failure code="404">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "data": {}}
    </on-failure>
    <on-failure code="404">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "no such user"}
    </on-failure>
    <on-failure code="403">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168"}
    </on-failure>
  </response>
</route>
```
---

#### Task Delete API
- delete a todo task
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<route>
  <url>
    /api/tasks/1234-5678-9012-3456
  </url>
  <method>
    PUT
  </method>
  <description>
    update a single todo task by id which associated to a current logged in user
  </description>
  <request using="header">
    header={"authorization": "token"}
  </request>
  <response>
    <on-success code="200">
      data={"status": "success", "timestamp": "2021-09-19T22:33:20.844168"}, headers={"authorization": "token"}
    </on-success>
    <on-failure code="404">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "data": {}}
    </on-failure>
    <on-failure code="404">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168", "reason": "no such user"}
    </on-failure>
    <on-failure code="403">
      data={"status": "fail", "timestamp": "2021-09-19T22:33:20.844168"}
    </on-failure>
  </response>
</route>
```

---
### `Database Schema`
Simple connect to `todo-tasks.db`, no auth required.
We suggest opens the db connection using `DB Browser for SQLite`,
download from here -> https://sqlitebrowser.org/dl

- We have only one Table `todos`.
- The `ToDos` datatype module located at package `modules/datatypes.py` represented by `SQLAlchemy` as an ORM,
We suggests using the `SQLAlchemy` API Docs for more information from here -> https://docs.sqlalchemy.org/en/13/index.html

