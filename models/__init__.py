from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import func

db = SQLAlchemy()
bcrypt = Bcrypt()

from models.user.Role import Role
from models.user.User import User
from models.classroom.Classroom import Classroom
from models.classroom.StudentClassroom import StudentClassroom
from models.subject.Subject import Subject
from models.exam.Exams import Exams
from models.exam.AnswerExams import AnswerExams
from models.exam.QuestionExams import QuestionExams