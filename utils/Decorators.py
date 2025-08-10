from functools import wraps
from flask import request, jsonify, current_app
from models.user import User
from utils.TokenHelper import TokenHelper
import jwt

class Decorator:

    def tokenRequired(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({'message': 'Token is missing or invalid format'}), 401
            
            token_parts = auth_header.split(" ")
            if len(token_parts) != 2:
                return jsonify({'message': 'Token format must be Bearer <token>'}), 401

            token = token_parts[1]
            decoded, error = TokenHelper.DecodeToken(token, token_type='access')
            if error:
                return jsonify({'message': error}), 401
            
            user = User.query.get(decoded['user_id'])
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            return f(user, *args, **kwargs)
        return decorated

    def rolesRequired(roleIdRequired):
        def wrapper(f):
            @wraps(f)
            def decorated(current_user ,*args, **kwargs):
                role_id = current_user.role_id
                if role_id != roleIdRequired:
                    return jsonify({'message': 'Access denied!'}), 403
                return f(current_user ,*args, **kwargs)
            return decorated
        return wrapper

    def extractTokenFromHeader():
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer'):
            return auth_header.split(' ')[1]
        return None

    def decodeToken(token):
        secret_key = current_app.config.get('ACCESS_TOKEN_SECRET_KEY')
        return jwt.decode(token, secret_key, algorithms=['HS256'])

    
       
