from models import db
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey

class ExamAttempt(db.Model):
    __tablename__ = 'exam_attempts'

    id = db.Column(db.Integer, primary_key=True)

    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=True)
    score = db.Column(db.Float, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    exam_answers = db.relationship('ExamAnswer', backref='attempt', lazy=True)
    exam = db.relationship('Exams', back_populates='attempts')