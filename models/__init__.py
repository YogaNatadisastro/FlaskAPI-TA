from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import func

db = SQLAlchemy()
bcrypt = Bcrypt()

from models.role import Role
from models.user import User
from models.classroom import Classroom
from models.student_classroom import StudentClassroom