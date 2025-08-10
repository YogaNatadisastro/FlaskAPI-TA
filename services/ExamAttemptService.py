import requests
from models import db
from models.exam.ExamAttempt import ExamAttempt
from datetime import datetime
from config.config import Config
from flask import current_app
from models.user.User import User
from models.exam.Exams import Exams

class ExamAttemptService:
    def __init__(self):
        self.post_url = Config.EXAM_BASE_URL

    def submitExamAttempt(self, data):
        user_id = data.get('user_id')
        exam_id = data.get('exam_id')
        answers = data.get('answers')

        if not user_id or not exam_id or not answers:
            raise ValueError("Missing required fields: user_id, exam_id, or answers")
        
        # get UUID from user and exam
        user = User.query.get(user_id)
        exam = Exams.query.get(exam_id)

        # Build request for external service
        external_request = {
            "studentID": user.uuid,
            "testID": exam.uuid,
            "answers": answers
        }

        # Send request to external service
        try:
            response = requests.post(
                f"{self.post_url}/answer/submit",
                json=external_request,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"External API request failed: {e}")
            raise ValueError("Failed to submit exam attempt to external service")
        
        