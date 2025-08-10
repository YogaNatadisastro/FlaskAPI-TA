from flask import Blueprint, jsonify
from services.GenerateQuestionResultService import GenerateQuestionResultService

questionResultBp = Blueprint("question_results", __name__)

@questionResultBp.route('/result/<string:job_id>', methods=['GET'])
def getGeneratedQuestionStatus(job_id):
    result = GenerateQuestionResultService.getQuestionByJobId(job_id)
    return jsonify(result), 200