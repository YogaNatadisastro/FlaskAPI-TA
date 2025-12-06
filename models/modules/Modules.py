from models import db
from datetime import datetime

class Modules(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(50), nullable=False)
    resource_name = db.Column(db.String(150), nullable=False)
    job_id = db.Column(db.String(100), nullable=True)

    classroom_id = db.Column(
        db.Integer,
        db.ForeignKey('classroom.id'),
        nullable=False
    )

    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploader = db.relationship('User', backref='uploaded_modules')
    classroom = db.relationship('Classroom', backref='modules')