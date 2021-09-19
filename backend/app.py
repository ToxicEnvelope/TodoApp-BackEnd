from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.logger import logger as fapi_logger

from backend.helpers import stamp, response_hex_id
from backend.database import db_session, db_init
from backend.helpers import Logger
from backend.enums import AppRoutes
from modules.datatypes import Records

import flows


log = Logger(fapi_logger)
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

############################################################################################################

@app.on_event('startup')
def start_db(retry=5):
    if retry == 0:
        log.error('error while creating a connection to database')
        exit()
    elif db_init():
        log.info('connection to database established successfully')
        return True
    retry -= 1
    return start_db(retry)

############################################################################################################

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = stamp()
    response: Response = await call_next(request)
    response.headers['x-process-time'] = '%s' % (stamp() - start_time)
    return response

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers['x-response-id'] = response_hex_id()
    return response

@app.middleware('http')
async def write_to_db(request: Request, call_next):
    response: Response = await call_next(request)
    record = Records(req_obj=request, resp_obj=response)
    db_session.add(record)
    db_session.commit()
    return response

############################################################################################################

@app.get(AppRoutes.Health.value)
async def health():
    return await flows.check.health()

@app.post(AppRoutes.Register.value)
async def register(request: Request):
    return await flows.session.registration(request, db_session, log)

@app.post(AppRoutes.Login.value)
async def login(request: Request):
    return await flows.session.authentication(request, db_session, log)

############################################################################################################

@app.get(AppRoutes.Tasks.value)
@flows.check.validate_token
async def get_all_tasks(request: Request):
    return await flows.user.get_tasks(request, db_session, log)

@app.post(AppRoutes.Tasks.value)
@flows.check.validate_token
async def create_new_tasks(request: Request):
    return await flows.user.create_task(request, db_session, log)

@app.get(AppRoutes.TaskById.value)
@flows.check.validate_token
async def get_tasks_by_id(request: Request, task_id):
    return await flows.user.get_task(task_id, request, db_session, log)

@app.put(AppRoutes.TaskById.value)
@flows.check.validate_token
async def update_tasks_by_id(request: Request, task_id):
    return await flows.user.update_task(task_id, request, db_session, log)

@app.delete(AppRoutes.TaskById.value)
@flows.check.validate_token
async def delete_tasks_by_id(request: Request, task_id):
    return await flows.user.delete_task(task_id, request, db_session, log)

############################################################################################################
