from datetime import datetime, timedelta

class ExamValidator:
    @staticmethod
    def parseDatetime(s):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid datetime format: {s}. Expected format: YYYY-MM-DDTHH:MM:SS")

    @staticmethod
    def validateInput(data):
        try:
            title = data.get("title")
            job_id = data.get("job_id")
            module_id = data.get("module_id")
            classroom_id = data.get("classroom_id")
            level = data.get("level")
            quiz_type = data.get("quiz_type")
            user_id = data.get("user_id")
            
            try:
                num_questions = int(data.get("num_questions", 0))
                duration = int(data.get("duration", 0))
            except ValueError:
                raise ValueError("Number of questions and duration must be integers")
            
            if not all([title, job_id, module_id, classroom_id, level, quiz_type, user_id]):
                raise ValueError("All fields are required")
            if num_questions <= 0:
                raise ValueError("Number must be greater than 0")
            if duration <= 0:
                raise ValueError("Duration must be greater than 0")
            
            start_time = ExamValidator.parseDatetime(data.get("start_time")) or datetime.utcnow()
            end_time = ExamValidator.parseDatetime(data.get("end_time")) or (start_time + timedelta(minutes=duration))

        except ValueError as e:
            raise ValueError(str(e))
        except Exception:
            raise ValueError("Format data is not valid")

        return title, job_id, module_id, classroom_id, level, quiz_type, num_questions, user_id, start_time, end_time, duration