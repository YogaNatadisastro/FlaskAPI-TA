from models import db

class StudentExamResult(db.Model):
    __tablename__ = 'exam_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.Foreignkey('exams.id'), nullable=False)
    score = db.Column(db.Float, nullable=True)
    
    user = db.relationship('User', backref='exam_result')
    exam = db.relationship('Exam', backref='exam_result')