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