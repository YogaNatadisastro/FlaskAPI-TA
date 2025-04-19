from models import db

class Classroom(db.Model):
    __tablename__ = 'classroom'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    enroll_key = db.Column(db.String(100), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref='classrooms')
    subject = db.relationship('Subject', backref='classrooms_list')

    def __repr__(self):
        return f"<Classroom {self.class_name} - Created by {self.user.username}>"