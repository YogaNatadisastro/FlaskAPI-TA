from models import db

class Subject(db.Model):
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(255), nullable=False, unique=True)
