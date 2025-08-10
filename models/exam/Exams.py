from models import db
from datetime import datetime
import uuid

class Exams(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    module_id = db.Column(db.Integer, nullable=False)
    job_id = db.Column(db.String(200), unique=True, nullable=False)
    level = db.Column(db.String(10), nullable=False)
    quiz_type = db.Column(db.String(50), nullable=False)
    classroom_id = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = db.relationship('ExamQuestion', backref='exam', lazy=True)
    attempts = db.relationship('ExamAttempt', backref='exam', lazy=True)