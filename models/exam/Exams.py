from models import db
from datetime import datetime
import uuid

class Exams(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    quiz_type = db.Column(db.String(50), nullable=False)
    created_by = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = db.relationship('ExamQuestion', back_populates='exam', lazy=True)
    attempts = db.relationship('ExamAttempt', back_populates='exam', lazy=True)
    
    classroom = db.relationship('Classroom', back_populates='exams')