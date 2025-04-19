from flask import Blueprint, request, jsonify
from models.exam.Exams import Exams
from models.exam.QuestionExams import QuestionExams
from models.exam.AnswerExams import AnswerExams
from models.exam.StudentExamResult import StudentExamResult
from models import db

examBp = Blueprint('exams', __name__)


