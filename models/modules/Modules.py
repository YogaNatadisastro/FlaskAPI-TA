from models import db

class Modules(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    resource_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    classroom = db.relationship('Classroom', backref='modules', lazy=True)

    def __repr__(self):
        return f"<ClassroomModule classroom_id={self.classroom_id}, resource_id={self.resource_id}>"