from models import db
from models.exam.Exams import Exams
from models.exam.ExamQuestion import ExamQuestion
from models.generated.QuestionGenerated import QuestionGenerated
from utils.ExamUtils import ExamUtils
from utils.ResponseHelper import errorResponse, successResponse
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
import traceback, json

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
        try:
            if not data.get("title") or not data.get("classroom_id") or not data.get("module_id") or not data.get("num_questions"):
                raise ValueError("Exam name and classroom_id must be required")
            
            module_id = int(data["module_id"])
            quiz_type = data.get("quiz_type")
            if not quiz_type:
                raise ValueError("quiz_type is required when create an exam")
            
            questions = ExamQuestion.query.filter_by(module_id=module_id).all()
            if not questions:
                raise ValueError("Exam must have at least 1 question")
            
            filteredQuestions = ExamUtils.filterQuestionsByType(questions, quiz_type)
            if not filteredQuestions:
                raise ValueError(f"No questions found for quiz_type={quiz_type}")
            if len(filteredQuestions) < int(data["num_questions"]):
                raise ValueError(f"Not enough questions of type {quiz_type}, availabel={len(filteredQuestions)}")

            exam = Exams(
                title = data.get("title"),
                description = data.get("description"),
                classroom_id = data.get("classroom_id"),
                created_by = user_id,
                start_time = datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None,
                end_time = datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
                duration = int(data["duration"]) if data.get("duration") else None,
                module_id = module_id,
                quiz_type = quiz_type
            )
            db.session.add(exam)
            db.session.flush()
            
            selectedQuestion = ExamUtils.selectRandomQuestions(
                filteredQuestions, int(data["num_questions"])
            )

            for q in selectedQuestion:
                newQuestionsExam = ExamQuestion(
                    exam_id = exam.id,
                    generated_id = q.generated_id,
                    module_id = q.module_id,
                    question_metadata = q.question_metadata,
                    question_data = q.question_data
                )
                db.session.add(newQuestionsExam)
            db.session.commit()

            return {
                "status": "success",
                "message": "Exam created successfully",
                "exam_id": exam.id,
                "num_questions": len(selectedQuestion),
                "quiz_type": quiz_type
            }, 201
        
        except(ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}, 400
        
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "message": "Unexpected error: " + str(e)
            }, 500

        
        except(ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            return {
                "status": "error",
                "message": str(e)
            }, 400
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "message": "Unexpected error: " + str(e)
            }, 500
    
    @staticmethod
    def getExamDetail(exam_id, current_user):
        try:
            exam = (
                Exams.query
                .options(joinedload(Exams.questions))
                .filter(Exams.id == exam_id)
                .first()
            )
            if not exam:
                return errorResponse("Exam not found", 404)
            
            examData = {
                "exam_id": exam.id,
                "title": exam.title,
                "classroom_id": exam.classroom_id,
                "duration": exam.duration,
                "start_time": exam.start_time,
                "end_time": exam.end_time,
                "quiz_type": exam.quiz_type,
            }

            questions = []
            for q in exam.questions:
                data = q.question_data
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except Exception:
                        data = {}
                elif not isinstance(data, dict):
                    data = {}

                quiz_type = data.get("quiz_type")

                options = None
                if quiz_type in ("multiple_choice", "multiple_choices"):
                    opt_map = {}
                    if data.get("option_a") is not None:
                        opt_map["A"] = data.get("option_a")
                    if data.get("option_b") is not None:
                        opt_map["B"] = data.get("option_b")
                    if data.get("option_c") is not None:
                        opt_map["C"] = data.get("option_c")
                    if data.get("option_d") is not None:
                        opt_map["D"] = data.get("option_d")
                    options = opt_map
                elif quiz_type == "true_false":
                    options = {"true": "True", "false": "False"}

                if current_user.role_id == 1: 
                    questions.append({
                        "id": q.id,
                        "question": data.get("question"),
                        "quiz_type": quiz_type,
                        "options": options,
                        "answer": data.get("answer")
                    })
                    
                elif current_user.role_id == 2:
                    questions.append({
                        "id": q.id,
                        "question": data.get("question"),
                        "quiz_type": quiz_type,
                        "options": options,
                    })
                else:
                    return errorResponse("Role not supported", 403)
            
            examData["questions"] = questions
            return successResponse("Exam detail fetched", examData)
        
        except Exception as e:
            traceback.print_exc()
            return errorResponse(str(e), 500)
    
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
