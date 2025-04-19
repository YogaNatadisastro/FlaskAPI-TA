from models import db

class Exams(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question_exams.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer_exams.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)

    