from flask import Blueprint

from routes.auth import auth_bp
from routes.roles import roleBp
from routes.classroom import classroomBp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(roleBp, url_prefix='/role')
api_bp.register_blueprint(classroomBp, url_prefix='/classrooms')
