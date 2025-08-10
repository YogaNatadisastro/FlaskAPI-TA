from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.ExamService import ExamService
from utils.Decorators import Decorator
from models.user.User import User
from models import db

examBp = Blueprint('exam', __name__)
examService = ExamService()

@examBp.route('/create', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def create_exam(current_user):
    try:
        data = request.get_json()
        data["user_id"] = current_user.id

        result = examService.create_exam(data)
        return jsonify(result), 201
    
    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
