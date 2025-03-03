from models import db

class Role(db.Model):
    __tablename__= 'roles'
    id = db.Column(db.BigInteger, primary_key=True)
    name_role = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship('User', backref='role', lazy=True)