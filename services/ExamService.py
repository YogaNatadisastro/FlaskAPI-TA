from flask import jsonify, request, current_app
from datetime import datetime, timedelta
from models import db
from dataclasses import dataclass
from models.exam.Exams import Exams
from models.exam.ExamQuestion import ExamQuestion
from models.generated.QuestionGeneratedResult import QuestionGeneratedResult
import random, json

@dataclass
class ExamInput:
    title: str
    job_id: str
    module_id: int
    classroom_id: int
    level: str
    quiz_type: str
    num_questions: int
    user_id: int
    start_time: datetime
    end_time: datetime
    duration: int


class ExamService:

    @staticmethod
    def _get_field(source, candidates):
        if not source:
            return None
        
        if isinstance(source, dict):
            for key in candidates:
                if key in source and source[key] != None:
                    return source[key]
            return None
        
        for key in candidates:
            if hasattr(source, key):
                val = getattr(source, key)
                if val != None:
                    return val
        return None

    @staticmethod
    def create_exam(request_data):
        key_cfg = current_app.config["QUESTION_KEY"]

        try:
            title = request_data.get("title_exam")
            job_id = request_data.get("job_id")
            module_id = request_data.get("module_id")
            classroom_id = request_data.get("classroom_id")
            level = request_data.get("level")
            quiz_type = request_data.get("quiz_type")
            num_questions = int(request_data.get("num_questions"))
            user_id = request_data.get("user_id")
            start_time_str = request_data.get("start_time")
            end_time_str = request_data.get("end_time")
            duration = request_data.get("duration")
        except (ValueError, TypeError):
            raise ValueError("Format data is not valid")
        
        def _parse_dt(s):
            if not s:
                return None
            try:
                return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return ValueError("date format is invalid, expected 'YYYY-MM-DO HH:MM:SS'")
        start_time = _parse_dt(start_time_str) or datetime.utcnow()
        end_time = _parse_dt(end_time_str) if end_time_str else (start_time + timedelta(hours=duration))

        if not all([title, job_id, classroom_id, module_id, level, quiz_type, num_questions > 0, user_id]):
            raise ValueError("All fields are required")
        
        #Get all question
        records = QuestionGeneratedResult.query.filter_by(
            job_id=job_id,
            level=level,
            quiz_type=quiz_type
        ).all()

        # Flatten all questions to list
        all_questions = []
        for rec in records:
            q_list = rec.questions
            if isinstance(q_list, str):
                try:
                    q_list = json.loads(q_list)
                except Exception as e:
                    current_app.logger.error(f"Failed parse JSON questions for record id={rec.id}: {e}")
                    q_list = []
            if isinstance(q_list, list):
                all_questions.extend(q_list)

        if len(all_questions) < num_questions:
            raise ValueError("Not enough questions available for the exam")

        selected_questions = random.sample(all_questions, num_questions)

        # Save exams and ExamQuestion on transaction
        exam = Exams(
            title=title,
            job_id=job_id,
            module_id=module_id,
            classroom_id=classroom_id,
            level=level,
            quiz_type=quiz_type,
            created_by=user_id,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        try:
            db.session.add(exam)
            db.session.flush()

            for q in selected_questions:
                qdict = None
                if hasattr(q, "questions") and q.questions:
                    if isinstance(q.questions, str):
                        try:
                            qdict = json.loads(q.questions)
                        except json.JSONDecodeError:
                            pass
                    elif isinstance(q.questions, dict):
                        qdict = q.questions
                
                if not qdict:
                    qdict = getattr(q, "__dict__", {})
                
                question_text = ExamService._get_field(qdict, key_cfg["Q_TEXT_KEYS"])
                if not question_text:
                    raise ValueError(f"Question text not found in question (id={getattr(q, 'id', None)})")
                
                options = ExamService._get_field(qdict, key_cfg["OPTIONS_KEYS"])
                if isinstance(options, str):
                    try:
                        options = json.loads(options)
                    except Exception:
                        options = [options]
                if not options:
                    options = []
        
                correct_answer = ExamService._get_attr(qdict, key_cfg["ANSWERS_KEYS"])    
                question_id = ExamService._get_attr(qdict, key_cfg["QID_KEYS"]) or getattr(q, "id", None)

                exam_question = ExamQuestion(
                    exam_id=exam.id,
                    question_id=question_id,
                    question_text=question_text,
                    options=options,
                    correct_answer=correct_answer
                )
                db.session.add(exam_question)
            
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            current_app.logger.error("Error creating exam: %s", exc)
            raise
