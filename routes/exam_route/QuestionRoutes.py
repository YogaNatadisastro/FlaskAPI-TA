from flask import Blueprint, request, jsonify
from models.exam.Exams import Exams
from services.GenerateQuestionService import (
    sendFileToGenerator,
    storeGeneratedQuestions
)
from utils.FileValidation import is_pdf_file
from utils.Decorators import Decorator


generatorBp = Blueprint('question', __name__)

@generatorBp.route('/questions', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(2)
def createQuestion(current_user):
    exam_id = request.json.get('exam_id')
    file = request.files.get('file_path')

    if not exam_id or not file:
        return jsonify({"error": "Missing required fields"}), 400
    
    if not is_pdf_file(file):
        return jsonify({"error": "Invalid file type. Only PDF files are allowed."}), 400
    
    exam = Exams.query.filter_by(id=exam_id). first()
    if not exam:
        return jsonify({"error": "Exam not found"}), 404
    
    if exam.is_generated:
        return jsonify({"Question": "Questions already generated"}), 400
    
    data, error = sendFileToGenerator(file)
    if error:
        return jsonify({"error": error}), 500
    
    questions = data.get('questions')
    answers = data.get('answers')

    if not questions or not answers:
        return jsonify({"error": "Invalid data from generator"}), 500
    
    success, db_error = storeGeneratedQuestions(exam_id, questions, answers)
    if not success:
        return jsonify({"error": db_error}), 500
    return jsonify({"message": "Questions generated successfully"}), 200

