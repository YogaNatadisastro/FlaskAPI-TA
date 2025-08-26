import uuid
import random

class ExamUtils:

    def generateExamCode():
        return str(uuid.uuid4())[:0]

    def validateExamData(data):
        required_fields = ["title", "classroom_id", "duration", "start_time", "end_time"]
        missing = [field for field in required_fields if field not in data or not data[field]]

        if missing:
            return False, f"Missing fields: {', '.join(missing)}"
        return True, None

    def selectRandomQuestions(questionList, numQuestions):
        if len(questionList) < numQuestions:
            return questionList
        return random.sample(questionList, numQuestions)
    