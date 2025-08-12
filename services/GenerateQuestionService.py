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
            
            # Get questions from result
            quiz_details_data = result_data.get("quiz_details", [])
            questions_data = data.get("questions", [])

            # Get inserted_questions
            inserted_questions_data = result_data.get("data", {}).get("inserted_questions", [])

            # Flatten if nested list
            if isinstance(inserted_questions_data, list):
                if len(inserted_questions_data) == 1 and isinstance(inserted_questions_data[0], list):
                    inserted_questions_data = inserted_questions_data[0]

            # get question_id from inserted_questions
            question_id_value = 0
            if inserted_questions_data and isinstance(inserted_questions_data, list) and len(inserted_questions_data) > 0:
                first_item = inserted_questions_data[0]
                if isinstance(first_item, dict):
                    question_id_value = first_item.get("question_id")
                    
            inserted_message_value = result_data.get("message", "")

            result_model = QuestionGeneratedResult(
                job_id=job_id,
                module_id=generate.module_id,
                question_id=question_id_value,
                level=generate.level,
                quiz_type=generate.quiz_type,
                status=result_data.get('status', 'pending'),
                result_message=result_data.get('result_message', ''),
                insert_message=inserted_message_value,
                inserted_questions=inserted_questions_data,
                quiz_details=quiz_details_data,
                questions=questions_data,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )

            db.session.add(result_model)
            db.session.flush()

            #If API can't provide question_id
            if not question_id_value:
                result_model.question_id = result_model.id
                current_app.logger.info(
                    f"[UpdateStatus] job_id: {job_id} question_id created in local: {result_model.question_id}"
                )

            generate.result_id = result_model.id
            saved_result = result_model

        db.session.commit()

        if saved_result:
            return {
                "job_id": saved_result.job_id,
                "module_id": saved_result.module_id,
                "level": saved_result.level,
                "quiz_type": saved_result.quiz_type,
                "question_id": saved_result.question_id,
                "inserted_questions": saved_result.inserted_questions,
                "quiz_details": saved_result.quiz_details,
                "questions": saved_result.questions,
                "status": saved_result.status
            }
        
        return data