from flask import Blueprint, request, jsonify
from models.classroom.StudentClassroom import StudentClassroom
from models.classroom import Classroom
from models import db
import datetime

studentClassroomBp = Blueprint('student', __name__)

@studentClassroomBp.route('/student-classroom', methods=['GET'])
def getAllStudentClassroom():
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
    return jsonify(result), 200


@studentClassroomBp.route('/student-classrooms/<int:id>', methods=['GET'])
def getStudentClassroom(id):
    sc = StudentClassroom.query.get_or_404(id)
    return jsonify({
        'id': sc.id,
        'user_id': sc.user_id,
        'classroom_id': sc.classroom_id, 
        'joined_at': str(sc.joined_at)
    }), 200


@studentClassroomBp.route('/student-classrooms', methods=['POST'])
def createStudentClassroom():
    data = request.get_json()
    user_id = data.get('user_id')
    # classroom_id = data.get('classroom_id')
    enroll_key = data.get('enroll_key')
    classroom = Classroom.query.filter_by(enroll_key=enroll_key).first()
    if not classroom:
        return jsonify({'error': 'Invalid enroll key'}), 400
    
    existing_entry = db.session.query(StudentClassroom).filter_by(
        user_id=user_id, 
        classroom_id=classroom.id
        ).first()
    if existing_entry:
        return jsonify({'error': 'Student already enrolled in this classroom'}), 400
    
    newSc = StudentClassroom(
        user_id=user_id,
        classroom_id=classroom.id,
        joined_at=datetime.datetime.utcnow()
    )
    db.session.add(newSc)
    db.session.commit()
    return jsonify({'message': 'Student successfully enrolled in the classroom'}), 201


@studentClassroomBp.route('/student-classrooms/<int:id>', methods=['PUT'])
def updateStudentClassroom(id):
    data = request.get_json()
    sc = StudentClassroom.query.get_or_404(id)

    sc.user_id = data.get('user_id', sc.user_id)
    sc.classroom_id = data.get('classroom_id', sc.classroom_id)
    if 'joined_at' in data:
        sc.joined_at = data['joined_at']

    db.session.commit()
    return jsonify({'message': 'Student-Classroom reliation updated successfully'}), 200


@studentClassroomBp.route('/student-classrooms/<int:id>', methods=['DELETE'])
def deleteStudentClassroom(id):
    sc = StudentClassroom.query.get_or_404(id)
    db.session.delete(sc)
    db.session.commit()
    return jsonify({'message': 'Student-Classroom relation deleted successfully'}), 200
