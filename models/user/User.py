from models import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    access_code = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.BigInteger, db.ForeignKey('roles.id'), nullable=False)
    
    role = db.relationship('Role', backref='users')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def __repr__(self):
        return f"<User {self.username} - Role {self.role.name_role}>"