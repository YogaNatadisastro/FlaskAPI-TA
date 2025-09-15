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
                "exam_title": exam.title,
                "exam_description": exam.description,
                "duration": exam.duration,
                "quiz_type": exam.quiz_type,
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
        
        questions = []
        for q in exam.questions:
            metadata = q.question_metadata or {}
            data = q.question_data or {}
            questions.append({
                "id": q.id,
                "job_id": metadata.get("job_id"),
                "module_id": metadata.get("module_id"),
                "resource_name": metadata.get("resource_name"),
                "question_id": data.get("question_id"),
                "question": data.get("question")
            })

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
    
    @staticmethod
    def getAllExam(classroom_id=None, user_id=None):
        try:
            query = Exams.query
            if classroom_id:
                query = query.filter_by(classroom_id=classroom_id)
            if user_id:
                query = query.filter_by(created_by=user_id)

            exams = query.all()
            result = []
            for exam in exams:
                result.append({
                    "id": exam.id,
                    "title": exam.title,
                    "description": exam.description,
                    "quiz_type": exam.quiz_type,
                    "module_id": exam.module_id,
                    "created_by": exam.created_by,
                    "classroom_id": exam.classroom_id,
                    "start_time": exam.start_time.isoformat() if exam.start_time else None,
                    "end_time": exam.end_time.isoformat() if exam.end_time else None,
                    "duration": exam.duration,
                    "created_at": exam.created_at.isoformat() if exam.created_at else None,
                    "updated_at": exam.updated_at.isoformat() if exam.updated_at else None,
                    "num_questions": len(exam.questions)
                })
            
            return result, 200
        except Exception as e:
            return {"error" : str(e)}, 500
