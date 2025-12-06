from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import func

db = SQLAlchemy()
bcrypt = Bcrypt()

from models.user.Role import Role
from models.user.User import User
from models.classroom.classroom import Classroom
from models.modules.Modules import Modules
from models.classroom.StudentClassroom import StudentClassroom
from models.subject.Subject import Subject
from models.exam.ExamAnswer import ExamAnswer
from models.exam.ExamAttempt import ExamAttempt
from models.exam.ExamQuestion import ExamQuestion
from models.exam.Exams import Exams
from models.generated.QuestionGenerated import QuestionGenerated
from models.token.RefreshToken import RefreshToken
from models.modules.ClassroomModels import ClassroomModule
