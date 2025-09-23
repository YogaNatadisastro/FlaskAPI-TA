from typing import Dict, Any, List

class MergeQuestion:
    @staticmethod
    def merge(detail_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        #combine inserted_question raw with question raw
        mergedQuestions = []

        insertedRaw = detail_response.get("result", {}).get("data", {}).get("inserted_questions", [])
        questionsRaw = detail_response.get("questions", [])

        mappingQuestionId = {}
        for item in insertedRaw:
            questionTextMerge = item.get("question")
            questionIdMerge = item.get("question_id")
            if questionTextMerge and questionIdMerge is not None:
                mappingQuestionId[questionTextMerge] = questionIdMerge

        for q in questionsRaw:
            questionTextMerge = q.get("question")
            questionIdMerge = mappingQuestionId.get(questionTextMerge)
            quizType = q.get("quiz_type") or "unknown"
            merged = {
                "question_id": questionIdMerge,
                "question": questionTextMerge,
                "quiz_type": quizType
            }

            for key in ("answer", "option_a", "option_b", "option_c", "option_d"):
                if key in q:
                    merged[key] = q[key]

            mergedQuestions.append(merged)

        return mergedQuestions