from flask import jsonify
from models.user import User
from utils.TokenHelper import TokenHelper
from models import db 

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
    
    
    def createUser(data):
        try:
            newUser = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                birth_date=data['birth_date'],
                username=data['username'],
                email=data['email'],
                password=TokenHelper.HashPassword(data['password']),
                role_id=data['role_id']
            )
            
            db.session.add(newUser)
            db.session.commit()
            return jsonify({
                'message': 'User successfully registered',
                'data': {
                    'id': newUser.id,
                    'first_name': newUser.first_name,
                    'last_name': newUser.last_name,
                    'birth_date': newUser.birth_date,
                    'username': newUser.username,
                    'email': newUser.email,
                    'role_id': {
                        'id': newUser.role_id,
                        'name': newUser.role.name_role
                    }
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500