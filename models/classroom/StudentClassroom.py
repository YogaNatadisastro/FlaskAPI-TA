from models import db

class StudentClassroom(db.Model):
    __tablename__ = 'student_classroom'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), name='fk_student_classroom_classroom_id' ,nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref='student_classrooms')
    classroom = db.relationship('Classroom', backref='students')
    exam = db.relationship('Exams', backref='student_classrooms')