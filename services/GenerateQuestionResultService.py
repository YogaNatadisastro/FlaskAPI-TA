from models.generated.QuestionGeneratedResult import QuestionGeneratedResult
from flask import abort
from typing import List, Dict, Any


class GenerateQuestionResultService:

    @staticmethod
    def getQuestionByJobId(job_id: str):
        result = QuestionGeneratedResult.query.filter_by(job_id=job_id).first_or_404(
            description=f"Job ID {job_id} not found"
        )

        return {
            "job_id": result.job_id,
            "question_id": result.question_id,
            "module_id": result.module_id,
            "level": result.level,
            "quiz_type": result.quiz_type,
            "questions": [
                GenerateQuestionResultService._format_question(result.quiz_details)
            ],
            "inserted_questions": [
                GenerateQuestionResultService._format_question(result.inserted_questions)
            ]
        }
    
    @staticmethod
    def _format_question(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted_questions = []
        for q in questions:
            quiz_type = q["quiz_type"]

            # Opsional fields based on quiz type
            options = {
                "multiple_choice": {
                    k: q.get(f"option_{k}") for k in ['a', 'b', 'c', 'd']
                }, 
                "true_false": {
                    "true": q.get("option_true", "True"),
                    "false": q.get("option_false", "False")
                },
            }.get(quiz_type)

            questions_data = {
                "quiz_type": quiz_type,
                "question": q.get("question"),
                "answer": q.get("answer")
            }

            if options:
                questions_data["options"] = options

            formatted_questions.append(questions_data)

        return formatted_questions
