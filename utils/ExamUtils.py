import uuid
import random
import json
from flask import current_app


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
    
    @staticmethod
    def calculateResult(questions, answers):
        questionsMap = {}
        for q in questions:
            try:
                qData = q.question_data
                if isinstance(qData, str):
                    qData = json.loads(qData)

                questionId = qData.get("question_id")
                questionText = qData.get("question")
                options = qData.get("options", [])
                correctAnswer = (
                    str(qData.get("answer")).strip().lower()
                    if qData.get("answer")
                    else None
                )

                if questionId:
                    questionsMap[int(questionId)] = {
                        "question_text": questionText,
                        "options": options,
                        "correct_answer": correctAnswer
                    }
            except Exception as e:
                current_app.logger.error(f"Failed to parse data") 
                continue
        
        correctCount = 0
        totalQuestions = len(answers)
        detailResults = []

        for ans in answers:
            questionId = ans["question_id"]
            selectedAnswer = str(ans["selected_answer"]).strip().lower()

            questionInfo = questionsMap.get(questionId)
            correctAnswer = questionInfo["correct_answer"] if questionInfo else None

            isCorrect = (selectedAnswer == correctAnswer)
            if isCorrect:
                correctCount += 1

            detailResults.append({
                "question_id": questionId,
                "question_text": questionInfo["question_text"] if questionInfo else None,
                "selected_answer": selectedAnswer,
                "correct_answer": correctAnswer,
                "is_correct": isCorrect
            })

        score = round((correctCount / totalQuestions) * 100, 2) if totalQuestions > 0 else 0.0

        return {
            "score": score,
            "correct": correctCount,
            "total": totalQuestions,
            "details": detailResults
        }    
    
    
    


    
    