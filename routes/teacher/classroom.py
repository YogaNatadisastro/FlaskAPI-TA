from flask import Blueprint, request, jsonify
from utils.Decorators import Decorator
from models.classroom.classroom import Classroom
from models import db

classroomBp = Blueprint('classroom', __name__)

@classroomBp.route('/classroom', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(2)
def getAllClassrooms(current_user):
    classrooms = Classroom.query.all()
    result = []
    for c in classrooms:
        result.append({
            'id': c.id,
            'class_name': c.class_name,
            'description': c.description,
            'enroll_key': c.enroll_key,
            'user': {
                'id': c.user.id,
                'username': c.user.username,
                'email': c.user.email
            } if c.user else None,
            'subject': {
                'id': c.subject.id,
                'name': c.subject.subject_name,
            } if c.subject else None
        })

        userInfo = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role_id": current_user.role_id
        }

    return jsonify({
        "user": userInfo,
        "classrooms": result
    }), 200


@classroomBp.route('/classrooms/<int:id>', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(2)
def getClassroom(current_user, id): 
    classroom = Classroom.query.get_or_404(id)
    return jsonify({
        'id': classroom.id,
        'class_name': classroom.class_name,
        'description': classroom.description,
        'enroll_key': classroom.enroll_key,
        'user': {
                'id': classroom.user.id,
                'username': classroom.user.username,
                'email': classroom.user.email
            } if classroom.user else None,
            'subject': {
                'id': classroom.subject.id,
                'name': classroom.subject.subject_name,
            } if classroom.subject else None
        }), 200


@classroomBp.route('/classrooms', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(2)
def createClassroom(current_user):
    data = request.get_json()
    newClassroom = Classroom(
        class_name=data.get('class_name'),
        description=data.get('description'),
        enroll_key=data.get('enroll_key'),
        user_id=current_user.id,
        subject_id=data.get('subject_id') 
    )
    db.session.add(newClassroom)
    db.session.commit()
    return jsonify({'message': 'Classroom created successfully'}), 201


@classroomBp.route('/classrooms/<int:id>', methods=['PUT'])
@Decorator.tokenRequired
@Decorator.rolesRequired(2)
def updateClassroom(current_user,id):
    data = request.get_json()
    classroom = Classroom.query.get_or_404(id) 

    classroom.class_name = data.get('class_name', classroom.class_name)
    classroom.description = data.get('description', classroom.description)
    classroom.enroll_key = data.get('enroll_key', classroom.enroll_key)
    classroom.user_id = data.get('user_id', classroom.user_id)
    classroom.subject_id = data.get('subject_id', classroom.subject_id)

    db.session.commit()
    return jsonify({'message': 'Classroom updated successsfully'}), 200


@classroomBp.route('/classrooms/<int:id>', methods=['DELETE'])
@Decorator.tokenRequired
@Decorator.rolesRequired(2)
def deleteClassroom(current_user, id):
    classroom = Classroom.query.get_or_404(id)
    db.session.delete(classroom)
    db.session.commit()
    return jsonify({'message': 'Classroom deleted successfully'}), 200