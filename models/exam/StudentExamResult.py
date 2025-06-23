from models import db

class StudentExamResult(db.Model):
    __tablename__ = 'exam_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_submitted = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float, nullable=True)
    
    from models.exam.Exams import Exams
    user = db.relationship('User', backref='exam_results')
    exam = db.relationship('Exams', backref='student_results')