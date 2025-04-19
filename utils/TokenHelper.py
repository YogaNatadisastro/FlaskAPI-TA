import jwt
import datetime
from flask import current_app

# Generate Access Token
def GenerateAccessToken(user_id, expires_in=15):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in),
        'iat': datetime.datetime.utcnow(),
        'type': 'access'
    }
    secret_key = current_app.config['ACCESS_TOKEN_SECRET_KEY']
    return jwt.encode(payload, secret_key, algorithm='HS256')

# Generate Refresh Token
def GenerateRefreshToken(user_id, expires_in=7):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expires_in),
        'iat': datetime.datetime.utcnow(),
        'type': 'refresh'
    }
    secret_key = current_app.config['REFRESH_TOKEN_SECRET_KEY']
    return jwt.encode(payload, secret_key, algorithm='HS256')

# Decode token (used to verify both access and refresh)
def DecodeToken(token, token_type='access'):
    secret_key = current_app.config['ACCESS_TOKEN_SECRET_KEY'] if token_type == 'access' else current_app.config['REFRESH_TOKEN_SECRET_KEY']
    try: 
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        if payload['type'] != token_type:
            raise jwt.InvalidTokenError("Token type mismatch")
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError as e:
        raise Exception(f'Invalid token: {str(e)}')