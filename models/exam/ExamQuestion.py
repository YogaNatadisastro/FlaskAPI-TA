from sqlalchemy import Column, Integer, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models import db

class ExamQuestion(db.Model):
    __tablename__ = 'exam_questions'

    id = db.Column(Integer, primary_key=True)
    exam_id = db.Column(db.Integer, ForeignKey('exams.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

