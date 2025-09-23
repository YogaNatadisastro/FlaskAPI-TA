from flask import Blueprint, request, jsonify
from services.exam.ExamService import ExamService
from utils.Decorators import Decorator

examBp = Blueprint('exams', __name__)
exam_service = ExamService()

@examBp.route('/create', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def createExam(current_user):
    data = request.get_json()
    response, status = exam_service.createExam(data, current_user.id)
    return jsonify(response), status

@examBp.route('/<int:exam_id>', methods=['GET'])
@Decorator.tokenRequired
def getExamDetail(current_user, exam_id):
    response, status = exam_service.getExamDetail(exam_id, current_user)
    return jsonify(response), status


@examBp.route('/all', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def getAllExams(current_user):
    try:
        classroom_id = request.args.get("classroom_id", type=int)
        user_id = current_user.id
        response, status = exam_service.getAllExam(classroom_id=classroom_id, user_id=user_id)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500
