from flask import current_app
from models.generated.QuestionGenerated import QuestionGenerated

class QuestionRepository:
    @staticmethod
    def getQuestions(job_id, level, quiz_type):
        questions = QuestionGenerated.query.filter_by(
            job_id=job_id,
            level=level,
            quiz_type=quiz_type
        ).all()
        current_app.logger.info(
            f"[Repository] Found {len(questions)} questions for job_id={job_id}, level={level}, quiz_type={quiz_type}"
        )
        return questions
