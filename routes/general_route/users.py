from flask import Blueprint, request, jsonify
from models.user import User
from services.UserService import UserService
from utils.Decorators import Decorator

userBp = Blueprint('user', __name__)
userService = UserService()


@userBp.route('update/username', methods=['PUT'])
@Decorator.tokenRequired
def updateUsername(current_user):
    data = request.get_json()
    new_username = data.get('username')
    
    return userService.updateUsername(
        user_id=current_user.id,
        new_username=new_username
    )

@userBp.route('update/password', methods=['PUT'])
@Decorator.tokenRequired
def updatePassword(current_user):
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    return UserService.updatePassword(
        user_id=current_user.id,
        old_password=old_password,
        new_password=new_password
    )

##Not used for now 
##
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

