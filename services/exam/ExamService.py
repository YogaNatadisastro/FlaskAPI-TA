from models import db
from models.exam.Exams import Exams
from models.exam.ExamQuestion import ExamQuestion
from models.generated.QuestionGenerated import QuestionGenerated
from utils.ExamUtils import ExamUtils
from datetime import datetime

class ExamService:

    @staticmethod
    def validateExamData(data):
        required_fields = ["title", "classroom_id", "duration", "start_time", "end_time", "module_id", "quiz_type", "num_questions"]
        missing = [field for field in required_fields if field not in data or not data[field]]

        if missing:
            return False, f"Missing fields: {', '.join(missing)}"
        return True, None
    
    @staticmethod
    def createExam(data, user_id):
        valid, error = ExamService.validateExamData(data)
        if not valid:
            return {"error": error}, 400
        
        try:
            exam = Exams(
                title=data["title"],
                description=data.get("description"),
                module_id=data["module_id"],
                quiz_type=data["quiz_type"],
                classroom_id=data["classroom_id"],
                created_by=user_id,
                start_time=datetime.fromisoformat(data["start_time"]),
                end_time=datetime.fromisoformat(data["end_time"]),
                duration=int(data["duration"])
            )
            db.session.add(exam)
            db.session.flush()

            questions = QuestionGenerated.query.filter_by(module_id=data["module_id"]).all()
            if not questions:
                db.session.rollback()
                return {
                    "error": "No questions available for this module"
                }, 404
            
            selectedQuestions = ExamUtils.selectRandomQuestions(questions, int(data["num_questions"]))

            for q in selectedQuestions:
                eq = ExamQuestion(
                    exam_id = exam.id,
                    question_metadata={
                        "job_id": getattr(q, "job_id", None),
                        "module_id": q.module_id,
                        "resource_name": getattr(q, "resource_name", None),
                        "question_id": q.id
                    }
                )
                db.session.add(eq)
            db.session.commit()

            return {
                "message": "Exam created successfully",
                "exam_id": exam.id,
                "num_questions": len(selectedQuestions)
            }, 201
        
        except Exception as e:
            db.session.rollback()
            return {
                "error": str(e)
            }, 500
    
    
    @staticmethod
    def getExamDetail(exam_id):
        exam = Exams.query.get(exam_id)
        if not exam:
            return {"error": "Exam not found"}, 404
        
        questions = [
            {
                "id": q.id,
                "metadata": q.question_metadata,
                "data": q.question_data
            }
            for q in exam.questions
        ]

        return {
            "exam": {
                "id": exam.id,
                "title": exam.title,
                "description": exam.description,
                "duration": exam.duration,
                "start_time": exam.start_time.isoformat(),
                "end_time": exam.end_time.isoformat(),
                "questions": questions
            }
        }, 200