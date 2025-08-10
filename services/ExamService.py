from flask import jsonify, request
from datetime import datetime, timedelta
from models import db
from models.exam.Exams import Exams
from models.exam.ExamQuestion import ExamQuestion
from models.generated.QuestionGeneratedResult import QuestionGeneratedResult
import random

class ExamService:
    @staticmethod
    def create_exam(request_data):
        title = request_data.get("title_exam")
        job_id = request_data.get("job_id")
        module_id = request_data.get("module_id")
        classroom_id = request_data.get("classroom_id")
        level = request_data.get("level")
        quiz_type = request_data.get("quiz_type")
        num_questions = request_data.get("num_questions")
        user_id = request_data.get("user_id")

        start_time_str = request_data.get("start_time")
        end_time_str = request_data.get("end_time")
        duration = request_data.get("duration")

        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S") if start_time_str else None
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S") if end_time_str else None

        if not start_time:
            start_time = datetime.utcnow()
        if not duration:
            duration = 60
        if not end_time:
            end_time = start_time + timedelta(minutes=duration)

        # Validasi Awal
        if not all([title, job_id, classroom_id, level, quiz_type, num_questions, user_id, start_time, end_time, duration]):
            raise ValueError ("Semua field harus diisi")
        
        # Get questions from QuestionGeneratedResult
        questions = QuestionGeneratedResult.query.filter_by(
            job_id=job_id,
            level=level,
            quiz_type=quiz_type
        ).all()

        if len(questions) < num_questions:
            raise ValueError("Tidak cukup pertanyaan tersedia untuk kuis ini")
        
        selected_questions = random.sample(questions, num_questions)

        # Simpan ke tabel Exams
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
        db.session.add(exam)
        db.session.flush()

        # Simpan ke tabel ExamQuestion
        for q in selected_questions:
            exam_question = ExamQuestion(
                exam_id=exam.id,
                question_id=q.question_id,
                question_text=q.question_text,
                options=q.options,
                correct_answer=q.correct_answer,
            )
            db.session.add(exam_question)
        
        db.session.commit()
        return {
            "message": "Exam berhasil dibuat",
            "exam_id": exam.id
        }
    