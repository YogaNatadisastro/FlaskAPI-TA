import uuid
import random
import json

class ExamUtils:

    @staticmethod
    def generateExamCode(length: int = 0) -> str:
        return str(uuid.uuid4()).replace("-", "")[:length]
    
    @staticmethod
    def validateExamData(data):
        required_fields = [
            "title", 
            "classroom_id",
              "duration", 
              "start_time", 
              "end_time",
              "module_id", 
              "num_questions",
              "quiz_type"]
        missing = [field for field in required_fields if field not in data or not data[field]]

        if missing:
            return False, f"Missing fields: {', '.join(missing)}"
        return True, None
    
    @staticmethod
    def selectRandomQuestions(questionList, numQuestions):
        if not questionList:
            return []
        if len(questionList) < numQuestions:
            shuffled = questionList[:]
            random.shuffle(shuffled)
            return questionList
        return random.sample(questionList, numQuestions)
    
    @staticmethod
    def filterQuestionsByType(questions, quiz_type: str):
        filtered = []
        for q in questions:
            qData = q.question_data
            if isinstance(qData, str):
                try:
                    qData = json.loads(qData)
                except Exception:
                    qData = {}
            if(qData or {}).get("quiz_type") == quiz_type:
                filtered.append(q)
        return filtered
    
    

    
    