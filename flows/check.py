import jwt
from fastapi.logger import logger as fapi_logger
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from backend.enums import AppStates
from backend.helpers import now, Logger
from functools import wraps

log = Logger(fapi_logger)

############################################################################################################

async def health():
    log.info('checking server health status')
    return JSONResponse(content=jsonable_encoder({
        'status': AppStates.Success.value,
        'timestamp': now()
    }), status_code=200, media_type='application/json')

############################################################################################################

def validate_token(func, header='Authorization', prefix='Bearer '):
    @wraps(func)
    def wrapped(*args, **kwargs):
        request = kwargs.get('request') if 'request' in kwargs else None
        token = request.headers.get(header).replace(prefix, '')
        try:
            if not token:
                raise Exception
            data = __get_jwt_decode_data__(token)
            assert 'sub' in data
            log.info('Verified session data: %r' % data)
        except Exception:
            return JSONResponse(content=jsonable_encoder({
                'status': AppStates.Fail.value,
                'timestamp': now(),
                'reason': 'missing token'
            }), status_code=403, media_type='application/json')
        return func(*args, **kwargs)
    return wrapped

############################################################################################################

def __get_jwt_decode_data__(token):
    session_data = jwt.decode(
        jwt=token,
        key='wA-hKPtOY3HDrBU_PFiLeBE6CeNJ8j3cSMd14VAf11v7LVvxyatmHKKsylWSTNar0sr1VJNxoXYG9GwB-HaZcQ',
        algorithms='hs256'
    )
    return session_data
