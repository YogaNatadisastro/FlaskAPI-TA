from flask import Blueprint, request, jsonify, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
from utils.TokenHelper import TokenHelper
from models.user import User
from services.AuthService import AuthService
from models import db
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

# Constants
GURU_ROLE_ID = 2

# Refresh Token if expired
@auth_bp.route('/refresh-token', methods=['POST'])
def refreshToken():
    data = request.get_json()
    refreshToken = data.get('refresh_token')

    if not refreshToken:
        return {'message': 'Refresh token is required'}, 400
    
    return AuthService.handleRefreshToken(refreshToken)

# Validate access code for GURU role
def isValidAccessCode (role_id, access_code):
    if role_id == GURU_ROLE_ID:
        expected_access_code = current_app.config.get('GURU_ACCESS_CODE')
        return access_code == expected_access_code
    return True

def createUser(data):
    hashedPass = generate_password_hash(data['password'], method='pbkdf2:sha256')
    return User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        birth_date=data.get('birth_date'),
        username=data.get('username'),
        email=data.get('email'),
        password=hashedPass,
        role_id=data.get('role_id')
    )

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    
    #validate fields must be reaquired
    required_fields = ['first_name', 'last_name', 'birth_date', 'username', 'email', 'password', 'role_id']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({'message': f'Missing fields: {", ".join(missing_fields)}'}), 400
    
    role_id = data.get('role_id')
    access_code = data.get('access_code')

    if not isValidAccessCode(role_id, access_code):
        return jsonify({'message': 'Invalid access code'}), 401

    newUser = createUser(data)
    db.session.add(newUser)
    db.session.commit()

    return jsonify({
        'message' : 'User successfully registered',
        'data' : {
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


@auth_bp.route('/login', methods=['POST'])
def login():
    try: 
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message' : 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']

        user = User.query.filter(User.email.ilike(email)).first()
        if not user:
            return jsonify({'message' : 'User not found'}), 404
        
        if not check_password_hash(user.password, password):
            return jsonify({'message' : 'Invalid password'}), 401
        
        # Generate JWT Token
        access_token = TokenHelper.GenerateAccessToken(user.id, user.role_id)
        refresh_token = TokenHelper.GenerateRefreshToken(user.id, user.role_id)

        return jsonify({
            'message': 'Login successful',
            'user' : {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role_id': user.role_id
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'An error occurred during login', 'error': str(e)}), 500
    

@auth_bp.route('/logout', methods=['POST'])
def logout():
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 401
    
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200
