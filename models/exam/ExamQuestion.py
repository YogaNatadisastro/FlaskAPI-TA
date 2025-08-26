from datetime import datetime
from models import db
from sqlalchemy import ForeignKey

class ExamQuestion(db.Model):
    __tablename__ = 'exam_questions'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False, index=True)

    question_metadata = db.Column(db.JSON, nullable=True)
    question_data = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    exam = db.relationship("Exams", back_populates="questions")

    #Helper 
    @property
    def job_id(self):
        return (self.question_metadata or {}).get('job_id')
    
    @job_id.setter
    def job_id(self, value):
        m = dict(self.question_metadata or {})
        m['job_id'] = value
        self.question_metadata = m

    @property
    def module_id(self):
        return (self.question_metadata or {}).get('module_id')

    @module_id.setter
    def module_id(self, value):
        m = dict(self.question_metadata or {})
        m['module_id'] = value
        self.question_metadata = m

    @property
    def resource_name(self):
        return (self.question_metadata or {}).get('resource_name')
    
    @resource_name.setter
    def resource_name(self, value):
        m = dict(self.question_metadata or {})
        m['resource_name'] = value
        self.question_metadata = m
    
    @property
    def question_id(self):
        return (self.question_metadata or {}).get('question_id')
    
    def __repr__(self):
        return f"<ExamQuestion id={self.id} exam_id={self.exam_id} question_id={self.question_id}>"