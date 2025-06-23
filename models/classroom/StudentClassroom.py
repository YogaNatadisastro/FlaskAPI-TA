from models import db

class StudentClassroom(db.Model):
    __tablename__ = 'student_classroom'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'classroom_id'),
    )

    user = db.relationship('User', backref='student_classrooms')
    classroom = db.relationship('Classroom', backref='students')
