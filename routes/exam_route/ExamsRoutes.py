from flask import Blueprint, request, jsonify
from models.exam.Exams import Exams
from models.exam.StudentExamResult import StudentExamResult
from models.modules.Modules import Modules
from models.classroom.classroom import Classroom
from utils.Decorators import Decorator
from datetime import datetime, timedelta
from models import db

examBp = Blueprint('exam', __name__)


@examBp.route('/exams', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(2)
def createExam(current_user):
    tittle_exam = request.json.get('tittle_exam')
    classroom_id = request.json.get('classroom_id')
    module_id = request.json.get('module_id')
    duration = request.json.get('duration')

    if not all([tittle_exam, classroom_id, module_id]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        duration = int(duration)
    except ValueError:
        return jsonify({"error": "Invalid duration"}), 400
    
    classroom = Classroom.query.filter_by(id=classroom_id, user_id=current_user.id).first()
    if not classroom:
        return jsonify({"error": "Classroom not found"}), 404
    
    module = Modules.query.filter_by(id=module_id, classroom_id=classroom_id).first()
    if not module:
        return jsonify({"error": "Module not found"}), 404
    
    
    exam = Exams(
        
        tittle_exam=tittle_exam,
        classroom_id=classroom_id,
        module_id=module_id,
        duration=duration
    )

    db.session.add(exam)
    db.session.commit()

    userInfo = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role_id": current_user.role_id
    }

    return jsonify({
        "message": "Exam created successfully",
        "exam": {
            "id": exam.id,
            "tittle_exam": exam.tittle_exam,
            "classroom_id": exam.classroom_id,
            "module_id": exam.module_id,
            "is_generated": exam.is_generated,
            "duration": exam.duration,
            "craeted_by": userInfo
        }
    }), 201


@examBp.route('/start_exam', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def startExam(current_user):
    exam_id = request.json.get('exam_id')
    if not exam_id:
        return jsonify({"error": "exam_id is required"}), 400
    
    exam = Exams.query.filter_by(id=exam_id).first()
    if not exam:
        return jsonify({"error": "Exam not found"}), 404
    
    record = StudentExamResult.query.filter_by(
        user_id=current_user.id,
        exam_id=exam.id
    ).first()

    if record and record.start_time:
        return jsonify({
            "message": "Exam already started",
            "start_time": record.start_time.isoformat(),
            "end_time": record.end_time.isoformat(),
            "duration_minutes": exam.duration_minutes
        }), 200
    
    if not record:
        record = StudentExamResult(
            user_id = current_user.id,
            exam_id = exam_id
        )

    now = datetime.now()
    record.start_time = now
    record.end_time = now + timedelta(minutes=exam.duration)

    db.session.add(record)
    db.session.commit()

    return jsonify({
        "message": "Exam started successfully",
        "start_time": record.start_time.isoformat(),
        "end_time": record.end_time.isoformat(),
        "duration_minutes": exam.duration
    }), 200