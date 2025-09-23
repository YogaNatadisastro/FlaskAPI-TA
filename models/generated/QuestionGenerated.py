from models import db
from datetime import datetime

class QuestionGenerated(db.Model):
    __tablename__ = 'question_generated'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(100), unique=True, nullable=False)
    module_id = db.Column(db.Integer, nullable=False)
    resource_name = db.Column(db.String(255), nullable=False)
    quiz_type = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(10), nullable=False)
    num_questions = db.Column(db.Integer, nullable=False)
    context = db.Column(db.Text, nullable=True)
    response_payload = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending')

    exam_questions = db.relationship("ExamQuestion", back_populates="generated", lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    update_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QuestionGenerated id={self.id} resource_name={self.resource_name} quiz_type={self.quiz_type} level={self.level} num_questions={self.num_questions} context={self.context}>"
