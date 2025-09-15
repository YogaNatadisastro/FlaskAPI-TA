from flask import Blueprint, request, jsonify
from utils.Decorators import Decorator
from models.classroom.classroom import Classroom
from services.ClassroomService import ClassroomService
from models import db

classroomBp = Blueprint('classroom', __name__)
classroomService = ClassroomService()

@classroomBp.route('/classroom', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def getAllClassrooms(current_user):
    try:
        return classroomService.getAllClassrooms(current_user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@classroomBp.route('/classrooms/<int:id>', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def getClassroom(current_user, id): 
    try:
        return classroomService.getClassroomById(current_user, id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@classroomBp.route('/classrooms', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def createClassroom(current_user):
    try:
        return classroomService.createClassroom(current_user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@classroomBp.route('/classrooms/<int:id>', methods=['PUT'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
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
@Decorator.rolesRequired(1)
def deleteClassroom(current_user, id):
    classroom = Classroom.query.get_or_404(id)
    db.session.delete(classroom)
    db.session.commit()
    return jsonify({'message': 'Classroom deleted successfully'}), 200