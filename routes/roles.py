from flask import Blueprint, request, jsonify
from models.role import Role
from models import db

roleBp = Blueprint('role', __name__)

@roleBp.route('/roles/all', methods=['GET'])
def get_roles():
    role = Role.query.all()
    result = []
    for r in role:
        result.append({
            'id': r.id,
            'name_role': r.name_role
        })
    return jsonify(result), 200

@roleBp.route('/roles/<int:id>', methods=['GET'])
def get_role(id):
    role = Role.query.get_or_404(id)
    return jsonify({
        'id': role.id,
        'name_role': role.name_role
    }), 200

@roleBp.route('/roles', methods=['POST'])
def created_role():
    data = request.get_json()
    new_role = Role(
        name_role=data.get('name_role')
    )
    db.session.add(new_role)
    db.session.commit()
    return jsonify({'message': 'Role created successfully'}), 201


