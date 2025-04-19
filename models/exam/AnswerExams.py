from models import db

class AnswerExams(db.Model):
    __tablename__ = 'answer_exams'
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(255), nullable=False)