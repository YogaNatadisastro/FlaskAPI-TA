from models import db
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey

class ExamAnswer(db.Model):
    __tablename__ = 'exam_answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('exam_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('exam_questions.id'), nullable=False)
    selected_answer = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)