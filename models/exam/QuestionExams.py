from models import db

class QuestionExams(db.Model):
    __tablename__ = 'question_exams'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)