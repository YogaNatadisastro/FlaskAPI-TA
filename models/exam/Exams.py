from models import db
from datetime import datetime

class Exams(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    tittle_exam = db.Column(db.String(100), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    is_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, nullable=True)  # Duration in minutes
    
    classroom = db.relationship("Classroom", backref="exams")
    module = db.relationship("Modules", backref="exams")
    