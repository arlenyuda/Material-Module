import jwt
import datetime
import json
import os
from jwt import ExpiredSignatureError, InvalidTokenError
from odoo.http import request, Response
from functools import wraps
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

def generate_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except ExpiredSignatureError:
        return {'error': 'Token expired', 'status': 401}
    except InvalidTokenError:
        return {'error': 'Invalid token', 'status': 401}

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header:
            return Response(json.dumps({'error': 'Missing token'}), status=401, content_type='application/json')

        token = auth_header.replace("Bearer ", "")
        result = decode_jwt(token)

        if isinstance(result, dict) and 'error' in result:
            return Response(json.dumps({'error': result['error']}), status=result['status'], content_type='application/json')

        user_id = result.get('user_id')
        request.uid = user_id
        request.env.user = request.env['res.users'].sudo().browse(user_id)

        return func(*args, **kwargs)
    return wrapper