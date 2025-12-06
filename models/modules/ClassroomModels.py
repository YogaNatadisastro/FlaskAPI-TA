from models import db

class ClassroomModule(db.Model):
    __tablename__ = 'classroom_modules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    classroom_id = db.Column(
        db.Integer, 
        db.ForeignKey('classroom.id', ondelete='CASCADE'),
        nullable=False
    )

    module_id = db.Column(
        db.Integer,
        db.ForeignKey('modules.id', ondelete='CASCADE'),
        nullable=False
    )

    classroom = db.relationship('Classroom', backref=db.backref('classroom_modules', cascade='all, delete-orphan'))
    module = db.relationship('Modules', backref=db.backref('classroom_modules', cascade='all, delete-orphan'))

    def toDict(self):
        return {
            "id": self.id,
            "classroom_id": self.classroom_id,
            "module_id": self.module_id
        }