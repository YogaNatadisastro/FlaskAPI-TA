from flask import Blueprint, request, jsonify
from models.user import User
from models import db
from werkzeug.security import generate_password_hash

userBp = Blueprint('user', __name__)

@userBp.route('/users', methods=['GET'])
def getAllUsers():
    users = User.query.all()
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'first_name': u.first_name,
            'last_name' : u.last_name,
            'birth_date': u.birth_date,
            'username': u.username,
            'email': u.email,
            'role': {
                'id': u.role.id,
                'name_role': u.role.name_role
            } if u.role else None
        })
    return jsonify(result), 200


@userBp.route('/users/<int:id>', methods=['GET'])
def getUserById(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'birth_date': user.birth_date,
        'username': user.username,
        'email': user.email,
        'role': {
            'id': user.role.id,
            'name_role': user.role.name_role
        } if user.role else None
    }), 200