import requests
from flask import Blueprint, request, jsonify
from models import db
from models.exam.QuestionExams import QuestionExams

qaBP = Blueprint('question', __name__)

@qaBP.route('/questions', methods=['POST'])
def createQuestion():
    data = request.get_json()
    question_text = data.get('module_id')