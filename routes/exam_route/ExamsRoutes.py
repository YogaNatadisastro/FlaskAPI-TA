from flask import Blueprint, request, jsonify
from services.exam.ExamService import ExamService
from services.exam.ExamGradingService import ExamGradingService
from utils.Decorators import Decorator
from flask import current_app
import traceback

examBp = Blueprint('exams', __name__)
exam_service = ExamService()
exam_attempt = ExamGradingService()

@examBp.route('/create', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def createExam(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid or empty JSON body"
            }), 400
        response, status = exam_service.createExam(data, current_user.id)
        return jsonify(response), status
    
    except Exception as e:
        current_app.logger.error("Unhandled exception in /exams/create", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Unexpected server error"
        }), 500

    
   
@examBp.route('/<int:exam_id>', methods=['GET'])
@Decorator.tokenRequired
def getExamDetail(current_user, exam_id):
    response, status = exam_service.getExamDetail(exam_id, current_user)
    return response, status

@examBp.route('/all', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1, 2)
def getAllExams(current_user):
    try:
        classroom_id = request.args.get("classroom_id", type=int)
        response, status = exam_service.getAllExam(
            classroom_id=classroom_id,
            user_id=current_user.id,
            role_id=current_user.role_id
        )
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@examBp.route('/<int:exam_id>', methods=['DELETE'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def deleteExam(current_user, exam_id):
    response, status = exam_service.deleteExam(exam_id, current_user)
    return jsonify(response), status


@examBp.route('/answer/submit', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(2)
def submitExamAttempt(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400
        
        current_app.logger.info(f"[ExamRoutes] Received exam submission: {data}")
        result = exam_service.submitExamAttempt(data)

        return jsonify({
            "message": result.get("message", "Exam submitted successfully"),
            "data": result.get("data", {})
        }), 200
    except ValueError as ve:
        current_app.logger.warning(f"[ExamRoute] Validation error: {ve}")
        return jsonify({"error": str(ve)}), 400
    
    except Exception as e:
        current_app.logger.error(f"[ExamRoute] Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@examBp.route('/attempts', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1, 2)
def getExamAttempts(current_user):
    try:
        exam_id = request.args.get("exam_id", type=int)
        classroom_id = request.args.get("classroom_id", type=int)

        user_id = None
        if current_user.role_id == 2:
            user_id = current_user.id

        return exam_service.getExamAttempts(
            exam_id=exam_id,
            user_id=user_id,
            classroom_id=classroom_id
        )
    
    except Exception as e:
        print(f"[Error] getExamAttempts: {e}")
        current_app.logger.error(f"Error in getExamAttempts: {e}")
        return jsonify({"error": str(e)}), 500
    
    
@examBp.route('/attempts/<int:attempt_id>', methods=['GET'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1, 2)
def getExamAttemptsDetail(current_user, attempt_id):
    return exam_service.getExamAttemptDetail(attempt_id, current_user)


    

