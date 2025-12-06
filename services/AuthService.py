from flask import jsonify, current_app
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.token.RefreshToken import RefreshToken
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
    
    @staticmethod
    def isValidAccessCode(role_id, access_code):
        GURU_ROLE_ID = 1
        if role_id == GURU_ROLE_ID:
            exceptedCode = current_app.config.get('GURU_ACCESS_CODE')
            return access_code == exceptedCode
        return True
    
    @staticmethod
    def createUser(data):
        try:
            requiredFields = [
                'first_name',
                'last_name',
                'birth_date',
                'username',
                'email',
                'password',
                'role_id'
            ]
            missingFields = [field for field in requiredFields if not data.get(field)]
            if missingFields:
                return jsonify({'message': f'Missing fields: {", ".join(missingFields)}'}), 400

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
        
    @staticmethod
    def login(data):
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']

        user = User.query.filter(User.email.ilike(email)).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid password'}), 401
        
        accessToken = TokenHelper.GenerateAccessToken(user.id, user.role_id)
        refreshToken = TokenHelper.GenerateRefreshToken(user.id, user.role_id)
        
        refresh_record = RefreshToken(
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        refresh_record.set_token(refreshToken)

        db.session.add(refresh_record)
        db.session.commit()

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'uuid': user.uuid,
                'email': user.email,
                'username': user.username,
                'role_id': user.role_id
            },
            'access_token': accessToken,
            'refresh_token': refreshToken,
            'expires_at': refresh_record.expires_at
        }), 200
    

    @staticmethod
    def logout(session):
        if 'user_id' not in session:
            return jsonify({'message': 'User not logged in'}), 401
        
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200

        