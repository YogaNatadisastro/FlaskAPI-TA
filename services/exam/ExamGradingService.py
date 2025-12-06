import json
import logging
from models import db, ExamAttempt, ExamQuestion

logger = logging.getLogger(__name__)

class ExamGradingService:

    @staticmethod
    def gradeAttempt(attempt_id: int):
        try:
            attempt = ExamAttempt.query.get(attempt_id)
            if not attempt:
                logger.error(f"[ExamGradingService] Attempt ID {attempt_id} not found")
                return {"Error": "Attempt not found"}, 404
            
            logger.info(f"[ExamGradingService] Start Grading {attempt_id}")

            questions = ExamQuestion.query.filter_by(exam_id = attempt.exam_id).all()
            if not questions:
                logger.error(f"[ExamGradingService] Question is not found ={attempt.exam_id}")
                return {"error": "No questions found for this exam"}
            
            questionMap = {}
            for q in questions:
                try:
                    questionData = q.question_data
                    if isinstance(questionData, str):
                        questionData = json.loads(questionData)
                    if not questionData:
                        continue

                    questionId = str(questionData.get("question_id"))
                    correct = str(questionData.get("correct_answer")).strip().lower()
                    questionMap[questionId] = correct
                
                except Exception as e:
                    logger.error(f"[ExamGradingService] Failed to parse question = {q.id}: {e}")
            
            studentAnswers = attempt.answers or []
            if isinstance(studentAnswers, str):
                try:
                    studentAnswers = json.loads(studentAnswers)
                except Exception:
                    studentAnswers = []

            if not studentAnswers:
                logger.warning(f"[ExamGradingService] Attempt Id {attempt_id} has no answers")
                return {"error": "No answers found it"}
            
            totalQuestions = len(studentAnswers)
            correctCount = 0
            detailedResult = []

            for ans in studentAnswers:
                questionId = str(ans.get("question_id"))
                selected = str(ans.get("selected_answer")).strip().lower()
                correct = questionMap.get(questionId)

                isCorrect = (selected == correct)
                if isCorrect:
                    correctCount += 1
                
                detailedResult.append({
                    "question_id": questionId,
                    "selected_answer": ans.get("selected_answer"),
                    "correct_answer": correct,
                    "is_correct": isCorrect
                })
            
            score = (correctCount / totalQuestions) * 100 if totalQuestions > 0 else 0.0
            score = round(score, 2)

            attempt.score = score
            attempt.status = "graded"
            attempt.external_response = {
                "summary": {
                    "correct": correctCount,
                    "total": totalQuestions,
                    "percentage": score
                },
                "details": detailedResult
            }

            db.session.commit()
            logger.info(f"[ExamGradingService] Grading completed for {attempt_id} with score = {score}")

            return {
                "message": "Grading Completed",
                "attempt_id": attempt_id,
                "exam_id": attempt.exam_id,
                "user_id": attempt.user_id,
                "score": score,
                "correct": correctCount,
                "total": totalQuestions,
                "percentage": score,
                "details": detailedResult
            }
        
        except Exception as e:
            logger.error(f"[ExamGradingService] Error grading attempt {attempt_id}: {e}")
            db.session.rollback()
            return {"error": str(e)}, 500
