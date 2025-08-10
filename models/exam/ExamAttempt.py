from models import db
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey

class ExamAttempt(db.Model):
    __tablename__ = 'exam_attempts'

    id = db.Column(db.Integer, primary_key=True)

    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)

    answers = db.relationship('ExamAnswer', backref='attempt', lazy=True)