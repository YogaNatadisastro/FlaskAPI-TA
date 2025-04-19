from functools import wraps
from flask import request, jsonify, current_app
import jwt

def extractTokenFromHeader():
    auth_header = request.headers.get('Authorization', None)
    if auth_header and auth_header.startswith('Bearer'):
        return auth_header.split(' ')[1]
    return None

def decodeToken(token):
    secret_key = current_app.config.get('ACCESS_TOKEN_SECERET_KEY')
    return jwt.decode(token, secret_key, algorithms=['HS256'])

def tokenRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extractTokenFromHeader()
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            payload = decodeToken(token)
            user_id = payload.get('user_id')
            role_id = payload.get('role_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(user_id=user_id, role_id=role_id, *args, **kwargs)
    
    return decorated

