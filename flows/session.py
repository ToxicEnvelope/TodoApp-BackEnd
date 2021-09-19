from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from werkzeug.security import generate_password_hash, check_password_hash
from backend.enums import AppStates
from backend.helpers import now, validate
from modules.datatypes import Users


############################################################################################################

async def registration(request, db_session, log):
    """
    Registration flows workflow
    :param request: Request object
    :param db_session: DatabaseConnection object
    :param log: Logger object
    :return: JSONResponse object
    """
    data = await request.json()
    if not data:
        log.warn('fail to register new user: missing request body %r' % data)
        return JSONResponse(content=jsonable_encoder({
            'status': AppStates.Fail.value,
            'timestamp': now(),
            'reason': 'missing body'
        }), status_code=400, media_type='application/json')

    if validate(data, 'register'):
        log.warn('fail to register new user: missing registration data %r' % data)
        return JSONResponse(content=jsonable_encoder({
            'status': AppStates.Fail.value,
            'timestamp': now(),
            'reason': 'missing registration data'
        }), status_code=400, media_type='application/json')

    email = data.get('email')
    opt_user = Users.query.filter_by(email=email).first()
    if opt_user:
        log.warn('fail to register new user: email %s is already exists' % email)
        return JSONResponse(content=jsonable_encoder({
            'status': AppStates.Fail.value,
            'timestamp': now(),
            'reason': 'email already in exists'
        }), status_code=401, media_type='application/json')
    del opt_user

    full_name = '%s %s' % (data.get('firstName'), data.get('lastName'))
    hashed_pwd = generate_password_hash(data.get('password'), method='sha256')
    user = Users(name=full_name, email=email, password=hashed_pwd)
    uid = user.id
    token = user.encode_auth_token(uid)
    user.token = token
    db_session.add(user)
    db_session.commit()
    log.info('registration successfully: %r' % data)
    log.info('registration successfully: new user %s was created' % uid)
    return JSONResponse(content=jsonable_encoder({
        'status': AppStates.Success.value,
        'timestamp': now(),
        'userId': uid,
        'message': 'registration successfully'
    }), status_code=201, headers={'Authorization': 'Bearer %s' % token}, media_type='application/json')

############################################################################################################

async def authentication(request, db_session, log):
    """
    Login flows workflow
    :param request: Request object
    :param db_session: DatabaseConnection object
    :param log: Logger object
    :return: JSONResponse object
    """
    data = await request.json()
    if not data:
        log.warn('fail to login new session: missing request body %r' % data)
        return JSONResponse(content=jsonable_encoder({
            'status': AppStates.Fail.value,
            'timestamp': now(),
            'reason': 'missing body'
        }), status_code=400, media_type='application/json')

    if validate(data, 'login'):
        log.warn('fail to login new session: missing login data %r' % data)
        return JSONResponse(content=jsonable_encoder({
            'status': AppStates.Fail.value,
            'timestamp': now(),
            'reason': 'missing login data'
        }), status_code=400, media_type='application/json')

    opt_user = Users.query.filter_by(email=data.get('email')).first()
    if (not opt_user) or (not check_password_hash(opt_user.password, data.get('password'))):
        log.warn('fail to login new session: incorrect usage of email and/or password %r' % data)
        return JSONResponse(content=jsonable_encoder({
            'status': AppStates.Fail.value,
            'timestamp': now(),
            'reason': 'incorrect email and/or password'
        }), status_code=401, media_type='application/json')

    user = opt_user
    del opt_user
    uid = user.id
    token = user.encode_auth_token(uid)
    user.token = token
    db_session.add(user)
    db_session.commit()
    log.info('login session successfully: %r' % data)
    log.info('login session successfully: user %s started a new session' % uid)
    return JSONResponse(content=jsonable_encoder({
        'status': AppStates.Success.value,
        'timestamp': now(),
        'userId': uid,
        'message': 'login successfully'
    }), status_code=200, headers={'Authorization': 'Bearer %s' % token}, media_type='application/json')

############################################################################################################