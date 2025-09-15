import requests, json
from flask import current_app
from sqlalchemy import cast, String
from datetime import datetime
from models import db
from models.generated.QuestionGenerated import QuestionGenerated
from models.exam.ExamQuestion import ExamQuestion
from config.config import Config
from flask_jwt_extended import get_jwt_identity

class GenerateQuestionService:
    def __init__(self):
        self.base_url = Config.GLOBAL_MODULE_URL

    def generateQuestions(self, request_data):
        url = f"{self.base_url}/generate_question"
        response = requests.post(url, json=request_data)
        response.raise_for_status()
        payload = response.json()
        job_id = payload.get("job_id")
        status = payload.get("status", "pending")

        # Simpan Record ke QuestionGenerated
        try:
            newGeneratedQuestion = QuestionGenerated(
                job_id = job_id,
                module_id = request_data['module_id'],
                resource_name = request_data['resource_name'],
                quiz_type = request_data['quiz_type'],
                level = request_data['level'],
                num_questions = request_data['num_questions'],
                context = request_data.get('context'),
                status = status,
            )
            db.session.add(newGeneratedQuestion)
            current_app.logger.info(f"[GenerateQuestions] job_id={job_id} status={status}")

            if status == "finished":
                extractedQuestions = self.extractQuestionsFromResponse(payload)
                self.persistQuestionsToExam(
                    exam_id=None,
                    job_id=job_id,
                    generateQuestion=newGeneratedQuestion,
                    questions=extractedQuestions
                )
            # Commit just once at the last
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            raise e
        return job_id
    
    
    def fetchExternalStatus(self, job_id: str) -> dict | None:
        url = f"{self.base_url}/generate_question/status/{job_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.warning(f"[FetchStatus] job_id={job_id} error={e}")
            return None
        

    def extractQuestionsFromResponse(self, response: dict) -> list:
        questions = []

        if not response or response.get("status") != "finished":
            return questions
        
        inserted = (
            response.get("result", {})
            .get("data", {})
            .get("inserted_questions", [])
        )
        quiz_details = response.get("result", {}).get("quiz_details", {})

        for idx, iq in enumerate(inserted):
            qd = quiz_details[idx] if idx < len(quiz_details) else {}
            questions.append({
                "question_id": iq.get("question_id"),
                "question": iq.get("question") or qd.get("question")
            })

        return questions
    
    
    def persistQuestionsToExam(self, exam_id: int, job_id: str, generate: QuestionGenerated, questions: list) -> bool:
        if not questions:
            current_app.logger.warning(f"[PersistQuestions] No questions to persist for job_id={job_id}")
            return False
        
        for q in questions:
            current_app.logger.info(f"[PersistQuestions] Saving question={q}")
            examQuestion = ExamQuestion(
                exam_id=exam_id,
                question_metadata={
                    "job_id": job_id,
                    "module_id": generate.module_id,
                    "resource_name": generate.resource_name
                },
                question_data={
                    "question_id": q["question_id"],
                    "question": q["question"]
                }
            )
            db.session.add(examQuestion)
        db.session.commit()
        return True


    def checkStatusOnly(self, job_id: str):
        data = self.fetchExternalStatus(job_id)
        if not data:
            raise ValueError("Failed to fetch status from external service")

        generate = QuestionGenerated.query.filter_by(job_id=job_id).first()
        if generate:
            generate.status = data.get('status', 'unknown')
            generate.updated_at = datetime.utcnow()
            db.session.commit()
    
    
    def updateQuestionGeneratedStatus(self, job_id:str, exam_id: int | None = None):
        data = self.fetchExternalStatus(job_id)
        if not data:
            raise ValueError("Failed to fetch status from external service")
        
        generate = QuestionGenerated.query.filter_by(job_id=job_id).first()
        if not generate:
            current_app.logger.warning(f"[UpdateStatus] job_id: {job_id} not found in database")
            return {"job_id": job_id, "status": data.get("status", "unknown")}
        
        # Update status
        generate.status = data.get('status', 'unknown')
        generate.response_payload = json.dumps(data, ensure_ascii=False)
        generate.updated_at = datetime.utcnow()
        status = generate.status
        saved_any = False

        if status == "finished":
            savedData = ExamQuestion.query.filter(
                cast(ExamQuestion.question_metadata['job_id'], String) == job_id
            ).first()

        if savedData:
            db.session.commit()
            return {
                "job_id": job_id,
                "status": status,
                "message": "Already finished previously. Status refreshed only"
            }
            
        if exam_id is None:
            db.session.commit()
            return {
                "job_id": job_id,
                "status": status,
                "message": "Finished. No exam_id provided, skipped persisting questions."
            }
            
        extractedQuestions = self.extractQuestionsFromResponse(data)
        saved_any = self.persistQuestionsToExam(exam_id, job_id, generate, extractedQuestions)
        
        db.session.commit()

        if saved_any:
            return {
                "job_id": job_id,
                "status": status,
                "message": "Finished. Questions have been saved"
            }
        return {"job_id": job_id, "status": generate.status}
    

    def getGenaratedQuestions(self, job_id):
        record = QuestionGenerated.query.filter_by(job_id=job_id).first()
        if not record:
            raise ValueError("JobId not found")
        
        if not record.response_payload:
            return {
                "message": "No questions found for this job yet", "questions": []
            }
        
        try:
            payload = json.loads(record.response_payload)
            questions = payload.get("questions", [])
            inserted_questions = (
                payload.get("result", {})
                .get("data", {})
                .get("inserted_questions", [])
            )
            quiz_details = payload.get("result", {}).get("get_details", [])

        except json.JSONDecodeError:
            current_app.logger.error(f"Invalid JSON in response_payload for job_id {job_id}")
            raise ValueError("Invalid JSON format in response_payload")
        
        return {
            "job_id": job_id,
            "status": record.status,
            "module_id": record.module_id,
            "questions": questions,
            "inserted_questions": inserted_questions,
            "quiz_details": quiz_details
        }
    
    def getAllQuestions(self):
        try: 
            records = ExamQuestion.query.all()
            questions = []
            for r in records:
                qd = r.question_data or {}
                questions.append({
                    "question_id": qd.get("question_id"),
                    "question": qd.get("question")
                })
            return questions
        except Exception as e:
            current_app.logger.error(f"[GetAllQuestions] error={e}")
            raise