from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models import db
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    
    hashPassword = generate_password_hash(data['password'], method='pbkdf2:sha256')

    newUser = User(
        full_name=data.get('full_name'),
        birth_date=data.get('birth_date'),
        username=data.get('username'),
        email=data.get('email'),
        password=hashPassword,
        role_id=data.get('role_id')
    )

    db.session.add(newUser)
    db.session.commit()

    return jsonify({'message': 'User successfully registered'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    
    user = User.query.filter_by(email=data.get('email')).first()
    if not user:
        return jsonify({'message': 'Invalid email or password'}), 401
    
    if not check_password_hash(user.password, data.get('password')):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, os.getenv('SECRET_KEY'), algorithm='HS256')

    return jsonify({'token': token}), 200