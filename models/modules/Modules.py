from models import db

class Modules(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)

    classroom = db.relationship('Classroom', backref='modules')

    def __repr__(self):
        return f"<Module {self.module_name}>"