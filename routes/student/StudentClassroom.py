from flask import Blueprint, request, jsonify
from models.classroom.StudentClassroom import StudentClassroom
from models.classroom.classroom import Classroom
from utils.Decorators import Decorator
from models import db
import datetime

studentClassroomBp = Blueprint('student', __name__)

@studentClassroomBp.route('/student-classroom', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def getAllStudentClassroom(current_user):
    sc_list = StudentClassroom.query.all()
    result = []
    for sc in sc_list:
        result.append({
            'id': sc.id,
            'user_id': sc.user_id,
            'classroom': {
                'id': sc.classroom.id,
                'class_name': sc.classroom.class_name,
                'description': sc.classroom.description
            },
            'joined_at': str(sc.joined_at)
        })

        userInfo = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role_id": current_user.role_id
        }

    return jsonify({
        "user": userInfo,
        "student_classrooms": result
    }), 200


# Not usefull
@studentClassroomBp.route('/student-classrooms/<int:user_id>/<int:classroom_id>', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def getStudentClassroom(current_user, user_id, classroom_id):
    sc = StudentClassroom.query.filter_by(user_id=user_id, classroom_id=classroom_id).first_or_404()
    return jsonify({
        'user_id': sc.user_id, 
        'joined_at': str(sc.joined_at),
        'classroom': {
            'id': sc.classroom.id,
            'class_name': sc.classroom.class_name,
            'description': sc.classroom.description
        }
    }), 200


@studentClassroomBp.route('/student-classrooms', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def createStudentClassroom(current_user):
    data = request.get_json()
    enroll_key = data.get('enroll_key')
    classroom = Classroom.query.filter_by(enroll_key=enroll_key).first()
    if not classroom:
        return jsonify({'error': 'Invalid enroll key'}), 400
    
    existing_entry = db.session.query(StudentClassroom).filter_by(
        user_id=current_user.id, 
        classroom_id=classroom.id
        ).first()
    if existing_entry:
        return jsonify({'error': 'Student already enrolled in this classroom'}), 400
    
    newSc = StudentClassroom(
        user_id=current_user.id,
        classroom_id=classroom.id,
        joined_at=datetime.datetime.utcnow()
    )
    db.session.add(newSc)
    db.session.commit()
    return jsonify({'message': 'Student successfully enrolled in the classroom'}), 201

# Not usefull
@studentClassroomBp.route('/student-classrooms/<int:id>', methods=['PUT'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def updateStudentClassroom(current_user, id):
    data = request.get_json()
    sc = StudentClassroom.query.get_or_404(id)

    sc.user_id = data.get('user_id', sc.user_id)
    sc.classroom_id = data.get('classroom_id', sc.classroom_id)
    if 'joined_at' in data:
        sc.joined_at = data['joined_at']

    db.session.commit()
    return jsonify({'message': 'Student-Classroom reliation updated successfully'}), 200


@studentClassroomBp.route('/student-classrooms/<int:id>', methods=['DELETE'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def deleteStudentClassroom(current_user, id):
    sc = StudentClassroom.query.get_or_404(id)
    db.session.delete(sc)
    db.session.commit()
    return jsonify({'message': 'Student-Classroom relation deleted successfully'}), 200
