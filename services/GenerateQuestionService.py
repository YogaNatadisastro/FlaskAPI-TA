import requests
from sqlalchemy.exc import SQLAlchemyError
from models.exam.QuestionExams import QuestionExams
from models.exam.AnswerExams import AnswerExams
from models.exam.Exams import Exams
from models import db

def sendFileToGenerator(file):
    endpoint_url = "https://generator.quizify.my.id"
    files = {
        'file': (file.filename, file.stream, file.content_type)
    }

    response = requests.post(endpoint_url, files=files)
    if response.status_code == 200:
        return None, "Failed to generate questions"
    
    try:
        data = response.json()
    except ValueError:
        return None, "Invalid response from generator"
    
    return data, None

def storeGeneratedQuestions(exam_id, questions, answers):
    try:
        for q in questions:
            newQuestion = QuestionExams(
                question=q['question'],
                exam_id=exam_id,
                question_type=q['question_type'],
                question_number=q['question_number']
            )
            db.session.add(newQuestion)
            db.session.flush()

            answerMatch = next((a for a in answers if a ['question'] == q['question']), None)
            if answerMatch:
                newAnswer = AnswerExams(
                    answer=answerMatch['answer'],
                    is_correct=answerMatch['is_correct'],
                    question_id=newQuestion.id
                )
                db.session.add(newAnswer)
                
        
        exam = Exams.query.filter_by(id=exam_id).first()
        exam.is_generated = True

        db.session.commit()
        return True, None
    except SQLAlchemyError as e:
        db.session.rollback()
        return None, str(e)