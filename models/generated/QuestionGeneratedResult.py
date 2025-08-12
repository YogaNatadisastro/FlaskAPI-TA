from models import db
from datetime import datetime

class QuestionGeneratedResult(db.Model):
    __tablename__ = 'question_generated_result'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(200), unique=True)

    module_id = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(10), nullable=False)
    quiz_type = db.Column(db.String(50), nullable=False)

    status = db.Column(db.String(50), nullable=False, default='pending')
    inserted_questions = db.Column(db.JSON, nullable=False)

    quiz_details = db.Column(db.JSON, nullable=False)
    questions = db.Column(db.JSON, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)