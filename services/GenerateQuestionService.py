import requests, json
from flask import current_app
from sqlalchemy import cast, String
from datetime import datetime
from models import db
from models.generated.QuestionGenerated import QuestionGenerated
from models.exam.ExamQuestion import ExamQuestion
from utils.MergeQuestion import MergeQuestion
from config.config import Config
from flask_jwt_extended import get_jwt_identity
from typing import Optional, List, Dict, Any

class GenerateQuestionService:
    def __init__(self):
        self.base_url = Config.GLOBAL_MODULE_URL

    def generateQuestions(self, request_data: Dict[str, Any]) -> Optional[str]:
        url = f"{self.base_url}/generate_question"
        response = requests.post(url, json=request_data)
        response.raise_for_status()
        payload = response.json()
        job_id = payload.get("job_id")
        status = payload.get("status", "pending")

        # Simpan Record ke QuestionGenerated
        try:
            newGeneratedQuestion = QuestionGenerated(
                job_id = job_id,
                module_id = request_data['module_id'],
                resource_name = request_data['resource_name'],
                quiz_type = request_data['quiz_type'],
                level = request_data['level'],
                num_questions = request_data['num_questions'],
                context = request_data.get('context'),
                status = status,
                response_payload = json.dumps(payload, ensure_ascii=False)
            )
            db.session.add(newGeneratedQuestion)
            db.session.flush()
            current_app.logger.info(f"[GenerateQuestions] job_id={job_id} status={status}")

            if status == "finished":
                extractedQuestions = self.extractQuestionsFromResponse(payload)
                exam_id = request_data.get("exam_id")
                self.persistQuestionsToExam(exam_id, job_id, newGeneratedQuestion, extractedQuestions)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"[GenerateQuestions] error saving generated job {job_id}: {e}")
            raise 

        return job_id
    
    
    def fetchExternalStatus(self, job_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/generate_question/status/{job_id}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.warning(f"[FetchStatus] job_id={job_id} error={e}")
            return None
        

    def extractQuestionsFromResponse(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        questionsOut: List[Dict[str, Any]] = []
        if not response:
            return questionsOut
        
        # Try to detect finished status in different locations
        status = response.get("status") or response.get("result", {}).get("status")
        if status != "finished":
            return questionsOut

        fullQuestions = (
            response.get("questions")
            or response.get("result", {}).get("questions")
            or []
        )

        insertedQuestions = (
            response.get("inserted_questions")
            or response.get("result", {}).get("data", {}).get("inserted_questions", [])
            or []
        )

        for iq in insertedQuestions:
            questionText = iq.get("question")
            questionId = iq.get("question_id") or iq.get("id")
            questiontype = iq.get("quiz_type") or "unknown"

            fq = next((f for f in fullQuestions if f.get("question") == questionText), {})

            merged: Dict[str, Any] = {
                "question_id": questionId,
                "question": questionText,
                "quiz_type": questiontype
            }

            if fq.get("answer") is not None:
                merged["answer"] = fq.get("answer")
            elif fq.get("correct_answer") is not None:
                merged["answer"] = fq.get("correct_answer")

            #Multiple_Choice Handling
            if questiontype in ("multiple_choice", "multiple_choices"):
                options = {}
                for optionKey in ("option_a", "option_b", "option_c", "option_d"):
                    if fq.get(optionKey) is not None:
                        options[optionKey] = fq.get(optionKey)
                
                #Fill the Blank Handling
            elif questiontype == "fill_the_blank":
                ans = fq.get("answer")
                if isinstance(ans, list):
                    merged["answer"] = ans
                elif ans is not None:
                    merged["answer"] = [ans]

                #True_False Handling
            elif questiontype == "true_false":
                rawAns = fq.get("answer") or fq.get("correct_answer")
                if rawAns is not None:
                    if isinstance(rawAns, str):
                        merged["answer"] = rawAns.strip().lower() in ("true", "1", "yes")
                    else:
                        merged["answer"] = bool(rawAns)

            questionsOut.append(merged)
    
        return questionsOut
    
    def parseQuestionData(self, field_value):
        if not field_value:
            return {}
        if isinstance(field_value, dict):
            return field_value
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except Exception:
                return {}
        return {}

    def persistQuestionsToExam(
            self,
            exam_id: Optional[int],
            job_id: str,
            generate: QuestionGenerated,
            questions: List[Dict[str, Any]],
            existing_entries: Optional[List[ExamQuestion]] = None
        ) -> bool:
        
        if not questions:
            current_app.logger.info(f"[PersistiQuestions] No questions to persist for job_id={job_id}")
            return False
        
        try:
            if existing_entries is None:
                try:
                    existing_entries = ExamQuestion.query.filter(
                        cast(ExamQuestion.question_metadata['job_id'], String) == job_id
                    ).all()
                except Exception:
                    existing_entries = []
            
            for e in existing_entries:
                e.parsedData = self.parseQuestionData(e.question_data)

            freeEntries = [e for e in existing_entries if not e.question_data]
            current_app.logger.info(
                f"[PersistQuestions] job_id={job_id} existing_total={len(existing_entries)} free_slots={len(freeEntries)} incoming={len(questions)}"
            )
            saved_any = False

            for q in questions:
                qId = q.get("question_id")
                qText = q.get("question")
                qType = q.get("quiz_type") or "unknown"

                if not qId or not qText:
                    current_app.logger.warning(
                        f"[PersistQuestions] Skipped question because missing id/text: {q}" 
                    )
                    continue

                matchedEntry = None
                for e in existing_entries:
                    eData = getattr(e, "parseQuestionData", {}) or {}
                    if eData.get("question_id") and str(eData.get("question_id")) == str(qId):
                        matchedEntry = e
                        break
                
                if not matchedEntry and freeEntries:
                    matchedEntry = freeEntries.pop(0)

                meta_update = {
                    "job_id": job_id,
                    "module_id": generate.module_id,
                    "resource_name": generate.resource_name
                }
                if qId:
                    meta_update["question_id"] = qId

                qData = {
                    "question_id": qId,
                    "question": qText,
                    "quiz_type": qType
                }
                # attach choices/answer if present
                for k in ("option_a", "option_b", "option_c", "option_d", "answer"):
                    if q.get(k) is not None:
                        qData[k] = q.get(k)
                
                if matchedEntry:
                    current_app.logger.info(f"[PersistQuestions] Updating existing ExamQuestion id={matchedEntry.id} qId={qId}")
                    # update explicit columns too
                    matchedEntry.generated_id = generate.id if getattr(generate, "id", None) else matchedEntry.generated_id
                    matchedEntry.module_id = generate.module_id
                    matchedEntry.exam_id = exam_id
                    # update metada object
                    meta = matchedEntry.question_metadata or {}
                    if isinstance(meta, str):
                        try:
                            meta = json.loads(meta)
                        except Exception:
                            meta = {}
                    meta.update(meta_update)
                    matchedEntry.question_metadata = meta
                    matchedEntry.question_data = qData
                    saved_any = True
                else:
                    current_app.logger.info(f"[PersistQuestions] Creating new ExamQuestion qid={qId}")
                    newMeta = meta_update.copy()
                    if qId:
                        newMeta["question_id"] = qId
                    
                    examQuestion = ExamQuestion(
                        exam_id = exam_id,
                        generated_id = generate.id if getattr(generate, "id", None) else None,
                        module_id = generate.module_id,
                        question_metadata = newMeta,
                        question_data = qData
                    )
                    db.session.add(examQuestion)
                    saved_any = True
            return saved_any
        
        except Exception as e:
            current_app.logger.error(f"[PersistQuestion] unexpected error:{e}", exc_info=True)
            raise

    def checkStatusOnly(self, job_id: str):
        data = self.fetchExternalStatus(job_id)
        if not data:
            raise ValueError("Failed to fetch status from external service")

        generate = QuestionGenerated.query.filter_by(job_id=job_id).first()
        if generate:
            generate.status = data.get('status', 'unknown')
            generate.update_at = datetime.utcnow()
            db.session.commit()

    
    def updateQuestionGeneratedStatus(
            self,
            job_id:str,
            exam_id: Optional[int] = None,
            generate: Optional[QuestionGenerated] = None,
            detail_response: Optional[Dict[str, Any]] = None ,
            existing_entries: Optional[List[ExamQuestion]] = None
        ) -> Dict[str, Any]:
        
        if generate is None:
            generate = QuestionGenerated.query.filter_by(job_id=job_id).first()
            if not generate:
                return {"job_id": job_id, "status": "not_found", "questions_saved": False }
        
        if detail_response is None:
            detail_response = self.fetchExternalStatus(job_id)
            if not detail_response:    
                return {"job_id": job_id, "status": "not_found", "questions_saved": False }
        
        generate.status = detail_response.get("status", generate.status)
        generate.response_payload = json.dumps(detail_response, ensure_ascii=False)
        generate.update_at = datetime.utcnow()
        db.session.commit()

        if generate.status != "finished":
            return {
                "job_id": job_id,
                "status": generate.status,
                "questions_saved": False
            }
        
        questions = MergeQuestion.merge(detail_response)
        if not questions:
            return {"job_id": job_id, "status": generate.status, "questions_saved": False }
        
        saved_any = self.persistQuestionsToExam(exam_id, job_id, generate, questions, existing_entries)
        db.session.commit()

        return {
            "job_id": job_id,
            "status": generate.status,
            "questions_saved": saved_any
        }
       

    def getGenaratedQuestions(self, job_id: str) -> Dict[str, Any]:
        record = QuestionGenerated.query.filter_by(job_id=job_id).first()
        if not record:
            raise ValueError("JobId not found")
        
        if record.status == "pending":
            fresh = self.fetchExternalStatus(job_id)
            if fresh:
                record.status = fresh.get("status", record.status)
                record.response_payload = json.dumps(fresh, ensure_ascii=False)
                record.update_at = datetime.utcnow()
                db.session.commit()
                return fresh
        
        try:
            payload = json.loads(record.response_payload)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in response_payload")
        
        return payload
    
    def getAllQuestions(self):
        try: 
            records = ExamQuestion.query.filter(ExamQuestion.question_data.isnot(None)).all()
            questions = []

            for r in records:
                qd = r.question_data 
                if isinstance(qd, str):
                    try:
                        qd = json.loads(qd)
                    except Exception as e:
                        current_app.logger.warning(f"[GetAllQuestion] JSON parse error: {e}")
                        qd = {}
                
                if not isinstance(qd, dict):
                    qd = {}

                questionResponse = {
                    "question_id": qd.get("question_id"),
                    "question": qd.get("question"),
                    "module_id": r.module_id,
                    "quiz_type": qd.get("quiz_type")
                }

                if "answer" in qd:
                    questionResponse["answer"] = qd["answer"]

                for opt in ("option_a", "option_b", "option_c", "option_d"):
                    if qd.get(opt) is not None:
                        questionResponse[opt] = qd[opt]

                questions.append(questionResponse)

            return questions
        except Exception as e:
            current_app.logger.error(f"[GetAllQuestions] error={e}")
            raise