from flask import jsonify
from models.user import User
from utils.TokenHelper import TokenHelper

class AuthService:

    @staticmethod
    def handleRefreshToken(referesh_token):
        payload, error = TokenHelper.DecodeToken(referesh_token)
        if error:
            return jsonify({'error': error}), 401
        
        user_id = payload.get('user_id')
        role_id = payload.get('role_id')

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        newAccessToken = TokenHelper.GenerateAccessToken(user_id, role_id)

        return jsonify({
            'access_token': newAccessToken
        }), 200