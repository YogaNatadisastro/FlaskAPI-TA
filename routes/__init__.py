from flask import Blueprint

from routes.users import userBp
from routes.auth import auth_bp
from routes.roles import roleBp
from routes.classroom import classroomBp
from routes.student_classroom import studentClassroomBp
from routes.SubjectRoutes import subjectBp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(userBp, url_prefix='/user')
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(roleBp, url_prefix='/role')
api_bp.register_blueprint(classroomBp, url_prefix='/classrooms')
api_bp.register_blueprint(studentClassroomBp, url_prefix='/student')
api_bp.register_blueprint(subjectBp, url_prefix='/subject')
