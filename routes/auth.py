from flask import Blueprint, request, jsonify, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
from utils.TokenHelper import GenerateAccessToken, GenerateRefreshToken, DecodeToken
from models.user import User
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
    try:
        data = request.get_json()
        refreshToken = data.get('refresh_token')

        if not refreshToken:
            return jsonify({'message': 'Refresh token is required'}), 400
        
        # Decode the refresh token
        decoded = DecodeToken(refreshToken, token_type='refresh')
        user_id = decoded.get('user_id')

        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Generate new access token
        newAccessToken = GenerateAccessToken(user.id)
        return jsonify({
            'access_token': newAccessToken
        }), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred during token refresh', 'error': str(e)}), 500

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

    return jsonify({'message': 'User successfully registered'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    try: 
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message' : 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message' : 'User not found'}), 404
        
        if not check_password_hash(user.password, password):
            return jsonify({'message' : 'Invalid password'}), 401
        
        # Generate JWT Token
        access_token = GenerateAccessToken(user.id)
        refresh_token = GenerateRefreshToken(user.id)

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
