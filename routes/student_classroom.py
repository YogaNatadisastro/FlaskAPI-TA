from flask import Blueprint, request, jsonify
from models.student_classroom import StudentClassroom
from models import db
import datetime

studentClassroomBp = Blueprint('student_classroom', __name__)

@studentClassroomBp.route('/student-classroom', methods=['GET'])
def getAllStudentClassroom():
    sc_list = StudentClassroom.query.all()
    result = []
    for sc in sc_list:
        result.append({
            'id': sc.id,
            'user_id': sc.user_id,
            'classroom_id': sc.classroom_id,
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
    newSc = studentClassroomBp(
        user_id = data.get('user_id'),
        classroom_id = data.get('classroom_id'),
        joined_at = data.get('joined_at', datetime.datetime.utcnow())
    )
    db.session.add(newSc)
    db.session.commit()
    return jsonify({'message': 'Student-Classroom relation created successfully'}), 201

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
