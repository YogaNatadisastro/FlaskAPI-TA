import requests
from flask import current_app
from datetime import datetime
from models import db
from models.generated.QuestionGenerated import QuestionGenerated
from models.generated.QuestionGeneratedResult import QuestionGeneratedResult
from config.config import Config
from flask_jwt_extended import get_jwt_identity

class GenerateQuestionService:
    def __init__(self):
        self.base_url = Config.GLOBAL_MODULE_URL

    def generateQuestions(self, request_data):
        url = f"{self.base_url}/generate_question"
        response = requests.post(url, json=request_data)
        response.raise_for_status()
        job_id = response.json().get('job_id')

        # current_user_id = get_jwt_identity()

        # Simpan Data ke Database
        newGeneratedQuestion = QuestionGenerated(
            job_id = job_id,
            module_id = request_data['module_id'],
            # user_id = current_user_id,
            resource_name = request_data['resource_name'],
            quiz_type = request_data['quiz_type'],
            level = request_data['level'],
            num_questions = request_data['num_questions'],
            context = request_data.get('context'),
            status = 'pending'
        )
        db.session.add(newGeneratedQuestion)
        db.session.commit()

        return job_id
    
    def updateQuestionGeneratedStatus(self, job_id):
        url = f"{self.base_url}/generate_question/status/{job_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            current_app.logger.warning(f"[UpdateStatus] job_id: {job_id} Error: {e}")
            raise ValueError("Failed to fetch status from external service")
        
        # Fetch from Database
        generate = QuestionGenerated.query.filter_by(job_id=job_id).first()
        if not generate:
            current_app.logger.warning(f"[UpdateStatus] job_id: {job_id} not found in database")
            return data
        
        # Update the status 
        generate.status = data.get('status', 'unknown')
        generate.updated_at = datetime.utcnow()

        # IF status is completed and result is already present
        if data.get("status") == "finished" and data.get("result"):
            result_data = data["result"]
            # Ambil questions direct from result_data
            questions_from_result = (
                result_data.get("quiz_details") or 
                data.get("questions") or
                []
            )
            
            inserted_questions_data = result_data.get("inserted_questions", [])

            

            result_model = QuestionGeneratedResult(
                job_id=job_id,
                module_id=generate.module_id,
                question_id=generate.id,
                level=generate.level,
                quiz_type=generate.quiz_type,
                status=result_data.get('status', 'pending'),
                result_message=result_data.get('result_message', ''),
                insert_message=result_data.get('insert_message', ''),
                inserted_questions=inserted_questions_data,
                quiz_details=result_data.get('quiz_details', {}),
                questions=questions_from_result,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )

            db.session.add(result_model)
            db.session.flush()
            generate.result_id = result_model.id
        
        db.session.commit()
        return data
