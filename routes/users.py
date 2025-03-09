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
            'full_name': u.full_name,
            'birth_date': u.birth_date,
            'username': u.username,
            'email': u.email,
            'role_id': u.role_id
        })
    return jsonify(result), 200


@userBp.route('/users/<int:id>', methods=['GET'])
def getUserById(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'id': user.id,
        'full_name': user.full_name,
        'birth_date': user.birth_date,
        'username': user.username,
        'emaol': user.email,
        'role_id': user.role_id
    }), 200