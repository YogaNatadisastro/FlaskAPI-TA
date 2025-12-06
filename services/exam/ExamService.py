from models import db
from flask import current_app
from models.exam.Exams import Exams
from models.user.User import User
from models.exam.ExamQuestion import ExamQuestion
from models.exam.ExamAttempt import ExamAttempt
from models.classroom.classroom import Classroom
from utils.ExamUtils import ExamUtils
from utils.ResponseHelper import errorResponse, successResponse, safeJsonLoads
from datetime import datetime, timedelta, timezone
from config.config import Config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
import traceback, json, requests, logging

logger = logging.getLogger(__name__)

class ExamService:
    def __init__(self):
        self.post_url = Config.EXAM_BASE_URL

    @staticmethod
    def validateExamData(data):
        required_fields = ["title", "classroom_id", "duration", "start_time", "end_time", "module_id", "quiz_type", "num_questions"]
        missing = [field for field in required_fields if field not in data or not data[field]]

        if missing:
            return False, f"Missing fields: {', '.join(missing)}"
        return True, None
    
    @staticmethod
    def parseIsoDateTime(value: str):
        if not value:
            return None
        try:
            if value.endswith('Z'):
                value = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception as e:
            raise ValueError(f"Invalid datetime format: {value}") from e
    
    @staticmethod
    def createExam(data, user_id):
        try:
            required = ["title", "classroom_id", "module_id", "num_questions", "quiz_type"]
            missing = [f for f in required if not data.get(f)]
            if missing:
                raise ValueError(f"Missing required fields: {', '.join(missing)}")
            
            try:
                module_id = int(data["module_id"])
                classroom_id = int(data["classroom_id"])
                num_questions = int(data["num_queestions"])
            except (TypeError, ValueError):
                raise ValueError("module_id, classroom_id and num_questions must be integers")
            
            if num_questions <= 0:
                raise ValueError("num_questions must be a positive integer")
            
            quiz_type = data.get("quiz_type")
            duration = None
            if data.get("duration") is not None:
                try:
                    duration = int(data["duration"])
                    if duration <= 0:
                        raise ValueError("duration must be a positive integer (minutes)")
                except (TypeError, ValueError):
                    raise ValueError("duration must be an integer (minutes)")
                
            start_time = ExamService.parseIsoDateTime(data.get("start_time")) if data.get("start_time") else None
            end_time = ExamService.parseIsoDateTime(data.get("end_time")) if data.get("end_time") else None

            if duration is not None and start_time and not end_time:
                end_time = start_time + timedelta(minutes=duration)

            if duration is not None and end_time and not start_time:
                start_time = end_time - timedelta(minutes=duration)
            
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
            
            selectedQuestion = ExamUtils.selectRandomQuestions(filteredQuestions, num_questions)
            new_exam_questions = []
            
            for q in selectedQuestion:
                new_exam_questions.append(
                    ExamQuestion(
                        exam_id = exam.id,
                        generated_id = q.generated_id,
                        module_id = q.module_id,
                        question_metadata = q.question_metadata,
                        question_data = q.question_data
                    )
                )
            db.session.add_all(new_exam_questions)
            db.session.commit()

            payload = {
                "status": "success",
                "message": "Exam created successfully",
                "exam_id": exam.id,
                "exam_title": exam.title,
                "num_questions": len(selectedQuestion),
                "quiz_type": quiz_type
            }
            return payload, 201
        
        except (ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            logger.exception("Failed to create exam")
            return {"status": "error", "message": str(e)}, 400
        
        except Exception as e:
            db.session.rollback()
            logger.exception("Unexpected error when creating exam")
            return {"status": "error", "message": "Unexpected error: " + str(e)}, 500
            
    
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

                question_id = data.get("question_id") or q.generated_id or q.id

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
                        "id": question_id,
                        "question": data.get("question"),
                        "quiz_type": quiz_type,
                        "answer": data.get("answer")
                    })
                    
                elif current_user.role_id == 2:
                    questions.append({
                        "id": question_id,
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
    def getAllExam(classroom_id=None, user_id=None, role_id=None):
        try:
            query = Exams.query
            if classroom_id:
                query = query.filter_by(classroom_id=classroom_id)
            if role_id == 1:
                query = query.filter_by(created_by=user_id)
            elif role_id == 2:
                pass

            exams = query.all()
            result = []
            for exam in exams:
                attempted = ExamAttempt.query.filter_by(
                    exam_id=exam.id,
                    user_id=user_id
                ).first() is not None

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
                    "num_questions": len(exam.questions),
                    "attempted": attempted
                })
            
            return result, 200
        except Exception as e:
            return {"error" : str(e)}, 500
        
    @staticmethod
    def deleteExam(exam_id, current_user):
        try:
            exam = Exams.query.filter_by(id=exam_id).first()
            if not exam:
                return errorResponse("Exam not found", 404)
            
            if exam.created_by != current_user.id:
                return errorResponse("You are not allowed to delete this exam", 403)
            
            ExamQuestion.query.filter_by(exam_id=exam_id).delete()
            db.session.delete(exam)
            db.session.commit()

            return successResponse("Exam deleted successfully")
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return errorResponse(str(e), 400)
        
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return errorResponse("Unexpected error: " + str(e), 500)
        
    ## Exam Attempt Related
    @staticmethod
    def submitExamAttempt(data):
        user_id = data.get('user_id')
        exam_id = data.get('exam_id')
        answers = data.get('answers')

        current_app.logger.info(f"Answers received: {answers} (type: {type(answers)})")
        
        if user_id is None or  exam_id is None or answers is None:
            raise ValueError("Missing required fields: user_id, exam_id, answers")
        
        user = User.query.get(user_id)
        exam = Exams.query.get(exam_id)

        if not user or not exam:
            raise ValueError("Useror Exam not found")
        current_app.logger.info(f"Processing exam attempt for user = {user.id}, exam = {exam.id}")

        existing_attempt = ExamAttempt.query.filter_by(
            user_id=user.id,
            exam_id=exam.id
        ).first()

        if existing_attempt:
            raise ValueError("Exam has already been attempted by this user")

        questions = ExamQuestion.query.filter_by(exam_id=exam_id).all()
        if not questions:
            raise ValueError(f"No questions found for exam_id = {exam_id}")
        
        formattedAnswers = []
        for ans in answers:
            questionId = str(ans.get("question_id") or ans.get("id"))
            selectedAnswer = ans.get("selectedAnswer") or ans.get("selected_answer")

            if not questionId or not selectedAnswer:
                raise ValueError(f"Invalid answer object: {ans}")
            
            formattedAnswers.append({
                "question_id": int(questionId),
                "selected_answer": str(selectedAnswer).strip().lower()
            })
        
        result = ExamUtils.calculateResult(questions, formattedAnswers)
        
        attempt = ExamAttempt(
            user_id = user.id,
            exam_id = exam.id,
            submitted_at = datetime.utcnow(),
            answers = formattedAnswers,
            score = result["score"],
            status = "graded",
        )

        db.session.add(attempt)
        db.session.commit()

        return {
            "message": "Exam submitted and graded successfully",
            "data" : {
                "attempt_id": attempt.id,
                "exam_id": exam.id,
                "user_id": user.id,
                **{k: result[k] for k in ("score", "correct", "total", "details")}
            }
        }
        
    @staticmethod
    def getExamAttempts(exam_id=None, user_id=None, classroom_id=None):
        try:
            query = (
                db.session.query(ExamAttempt)
                .join(ExamAttempt.exam)
                .join(Exams.classroom)
                .join(ExamAttempt.user)
            )
            
            if exam_id:
                query = query.filter(ExamAttempt.exam_id == exam_id)
            if user_id:
                query = query.filter(ExamAttempt.user_id == user_id)
            if classroom_id:
                query = query.filter(Exams.classroom_id == classroom_id)
            
            results = query.all()

            if not results:
                return successResponse("No exam attempts found", )
            
            formatted_results = []
            for attempt in results:
                formatted_results.append({
                    "attempt_id": attempt.id,
                    "exam_id": attempt.exam_id,
                    "exam_title": attempt.exam.title,
                    "quiz_type": attempt.exam.quiz_type,

                    "classroom": {
                        "id": attempt.exam.classroom.id,
                        "name": attempt.exam.classroom.class_name,
                        "description": attempt.exam.classroom.description
                    },

                    "user": {
                        "id": attempt.user.id,
                        "name": attempt.user.username,
                        "email": attempt.user.email
                    },

                    "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                    "answers": attempt.answers
                })
            
            return successResponse("Exam attempts fetched successfully", formatted_results)
        
        except Exception as e:
            traceback.print_exc()
            current_app.logger.error(f"Error fetching exam attempts: {e}")
            return errorResponse(str(e), 500)
        
    
    @staticmethod
    def getExamAttemptDetail(attempt_id, current_user):
        try:
            attempt = (
                db.session.query(ExamAttempt)
                .join(Exams, ExamAttempt.exam_id == Exams.id)
                .add_columns(
                    Exams.title.label("title"),
                    Exams.classroom_id.label("classroom_id"),
                    Exams.quiz_type.label("quiz_type")
                )
                .filter(ExamAttempt.id == attempt_id)
                .first()
            )

            if not attempt:
                return errorResponse("Exam attempt not found")
            
            attempt_data, exam_title, classroom_id, quiz_type = attempt

            if current_user.role_id == 2 and attempt_data.user_id != current_user.id:
                return errorResponse("Unauthorized to access this exam attempt")
            
            user = User.query.get(attempt_data.user_id)
            if not user:
                return errorResponse("User data not found")
            
            examQuestions = ExamQuestion.query.filter_by(exam_id=attempt_data.exam_id).all()

            questionMap = {
                int(safeJsonLoads(q.question_data)["question_id"]): safeJsonLoads(q.question_data)
                for q in examQuestions if q.question_data
            }

            answers = attempt_data.answers or []
            detailedResult = []

            for ans in answers:
                questionId = ans.get("question_id")
                answerSelected = str(ans.get("selected_answer")).strip().lower()
                questionData = questionMap.get(questionId, {})

                correctAnswer = str(questionData.get("answer", "")).strip().lower()
                isCorrect = answerSelected == correctAnswer

                detailedResult.append({
                    "question_id": questionId,
                    "question_text": questionData.get("question"),
                    "selected_answer": answerSelected,
                    "correct_answer": questionData.get("answer"),
                    "is_correct": isCorrect
                })
            
            result = {
                "attempt_id": attempt_data.id,
                "exam_id": attempt_data.exam_id,
                "exam_title": exam_title,
                "quiz_type": quiz_type,
                "classroom_id": classroom_id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": getattr(user, "email", None)
                },
                "score": attempt_data.score,
                "status": attempt_data.status,
                "submitted_at": attempt_data.submitted_at.isoformat() if attempt_data.submitted_at else None,
                "details": detailedResult
            }

            return successResponse("Exam attempt detail fetched successfully", result)
        
        except Exception as e:
            traceback.print_exc()
            current_app.logger.error(f"Error fetching exam attempt detail: {e}")
            return errorResponse(str(e))
    
    