from flask import Blueprint, request, jsonify, current_app, session
from services.AuthService import AuthService
from utils.Decorators import Decorator

auth_bp = Blueprint('auth', __name__)
authService = AuthService()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    return authService.createUser(data)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return authService.login(data)

