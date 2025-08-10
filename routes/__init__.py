from flask import Blueprint

from routes.general_route.users import userBp
from routes.general_route.auth import auth_bp
from routes.general_route.roles import roleBp
from routes.teacher.classroom import classroomBp
from routes.student.StudentClassroom import studentClassroomBp
from routes.SubjectRoutes import subjectBp
from routes.upload_module.ModuleRoutes import moduleBp
from routes.exam_route.ExamsRoutes import examBp
from routes.generate.GenerateQuestion import questionBp
from routes.generate.GenerateQuestionResultRoutes import questionResultBp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(userBp, url_prefix='/user')
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(roleBp, url_prefix='/role')
api_bp.register_blueprint(classroomBp, url_prefix='/classrooms')
api_bp.register_blueprint(studentClassroomBp, url_prefix='/student')
api_bp.register_blueprint(subjectBp, url_prefix='/subject')
api_bp.register_blueprint(moduleBp, url_prefix='/modules')
api_bp.register_blueprint(examBp, url_prefix='/exam')
api_bp.register_blueprint(questionBp, url_prefix='/questions')
api_bp.register_blueprint(questionResultBp, url_prefix='/question_results')