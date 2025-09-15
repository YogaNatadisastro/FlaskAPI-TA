from flask import Blueprint, request, jsonify, session
from models.subject import Subject
from utils.Decorators import Decorator
from models import db, Subject, User

subjectBp = Blueprint('subject', __name__)

def isTeacher(user):
    return user.role_id == 1

@subjectBp.route('/subjects', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def createSubject(current_user):
    user = User.query.get(current_user.id)
    if not isTeacher(user):
        return jsonify({'error': 'You are not authorized to create a subject'}), 403
    
    data = request.get_json()
    name = data.get('subject_name')
    if not name:
        return jsonify({'error': 'Subject name is required'}), 400
    
    newSubject = Subject(name=name, teacher_id=user.id)
    db.session.add(newSubject)
    db.session.commit()
    return jsonify({
        'message': 'Subject created successfully', "subject_id": newSubject.id
    }), 201

@subjectBp.route('/subjects', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def getAllSubjects(current_user):
    if current_user.role_id != 1:
        return jsonify({'error': 'Hanya guru yang dapat mengakses daftar subject'}), 403
    
    subjects = Subject.query.all()
    subjectList = [{
        'id': s.id,
        'subject_name': s.subject_name,
    } for s in subjects]
    return jsonify(subjectList), 200