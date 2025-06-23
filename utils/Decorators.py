from functools import wraps
from flask import request, jsonify, current_app
from models.user import User
import jwt

class Decorator:

    def tokenRequired(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            authHeader = request.headers.get('Authorization')
            if not authHeader:
                return jsonify({'message': 'Token is missing!'}), 401
            
            parts = authHeader.split()
            if parts[0].lower() != 'bearer' or len(parts) != 2:
                return jsonify({'message': 'Invalid token format!'}), 401
            
            token = parts[1]
            
            try:
                data = jwt.decode(token, current_app.config['ACCESS_TOKEN_SECRET_KEY'], algorithms=['HS256'])
                current_user = User.query.get (data['user_id'])
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired!'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token'}), 401
            
            return f(current_user, *args, **kwargs)
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

    
       
