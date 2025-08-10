from flask import Blueprint, request, jsonify
from utils.Decorators import Decorator
from services.GenerateQuestionService import GenerateQuestionService

questionBp = Blueprint('questions', __name__)
generator_service = GenerateQuestionService()

@questionBp.route('/generate_question', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def generateQuestion(current_user):
    data = request.get_json()
    try:
        job_id = generator_service.generateQuestions(data)
        return jsonify({"job_id": job_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@questionBp.route('/generate_question/status/<string:job_id>', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def getQuestionStatus(current_user, job_id):
    try:
        result = generator_service.updateQuestionGeneratedStatus(job_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500