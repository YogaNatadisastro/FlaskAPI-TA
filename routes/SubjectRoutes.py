from flask import Blueprint, request, jsonify, session
from models.subject import Subject
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from models import db, Subject, User


subjectBp = Blueprint('subject', __name__)

def isTeacher(user):
    return user.role_id == 2

@subjectBp.route('/subjects', methods=['POST'])
@jwt_required()
def createSubject():
    currentUserId = get_jwt_identity()
    user = User.query.get(currentUserId)
    
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
def getAllSubjects():
    if session.get('role_id') == 2:
        return jsonify({'error': 'Hanya guru yang dapat mengakses daftar subject'}), 403
    
    subjects = Subject.query.all()
    subjectList = [{
        'id': s.id,
        'subject_name': s.subject_name,
    } for s in subjects]
    return jsonify(subjectList), 200