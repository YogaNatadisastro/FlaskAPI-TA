import jwt
import datetime
from flask import current_app

class TokenHelper:

    _SECRET_KEY = {
        'access': 'ACCESS_TOKEN_SECRET_KEY',
        'refresh': 'REFRESH_TOKEN_SECRET_KEY'
    }

    # Generate Access Token
    @staticmethod
    def GenerateAccessToken(user_id, role_id):
        expires_in = current_app.config.get('ACCESS_TOKEN_EXPIRES_IN', 15)
        payload = {
            'user_id': user_id,
            'role_id': role_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in),
            'iat': datetime.datetime.utcnow(),
            'type': 'access'
    }
        secret_key = current_app.config['ACCESS_TOKEN_SECRET_KEY']
        return jwt.encode(payload, secret_key, algorithm='HS256')

    # Generate Refresh Token
    @staticmethod
    def GenerateRefreshToken(user_id, role_id):
        expires_in = current_app.config.get('REFRESH_TOKEN_EXPIRES_IN', 7)
        payload = {
            'user_id': user_id,
            'role_id': role_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expires_in),
            'iat': datetime.datetime.utcnow(),
            'type': 'refresh'
        }
        secret_key = current_app.config['REFRESH_TOKEN_SECRET_KEY']
        return jwt.encode(payload, secret_key, algorithm='HS256')

    # Decode token (used to verify both access and refresh)
    @staticmethod
    def DecodeToken(token, token_type='access'):
        secretKeyName = TokenHelper._SECRET_KEY.get(token_type)
        if not secretKeyName:
            return None, 'Invalid token type'
        
        secretKey = current_app.config.get(secretKeyName)
        if not secretKey:
            return None, 'Secret key not found in config'

        try:
            payload = jwt.decode(token, current_app.config['REFRESH_TOKEN_SECRET_KEY'], algorithms=['HS256'])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, 'Refresh token has expired'
        except jwt.InvalidTokenError:
            return None, 'Invalid refresh token'