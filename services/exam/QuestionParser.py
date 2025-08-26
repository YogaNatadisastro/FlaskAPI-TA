import json
from flask import current_app

class QuestionParser:
    @staticmethod
    def getField(source, candidates):
        if not source:
            return None
        if isinstance(source, dict):
            for key in candidates:
                if key in source and source[key] is not None:
                    return source[key]
                
            return None
        for key in candidates:
            if hasattr(source, key):
                val = getattr(source, key)
                if val is not None:
                    return val
        return None
    
    @staticmethod
    def parseQuestions(q, key_cfg):
        # Convert to dict
        try:
            q_id = getattr(q, 'id', None)
            current_app.logger.info(f"[Parser] Parsing Question record id={q_id}")

            # Get question text
            question_text = QuestionParser.getField(q, key_cfg("Q_TEXT_KEYS", []))

            # Get question option
            optionsRaw = QuestionParser.getField(q, key_cfg("OPTIONS_KEYS", []))
            options = []
            if optionsRaw:
                if isinstance(optionsRaw, str):
                    try:
                        options = json.loads(optionsRaw)
                        if not isinstance(options, list):
                            options = [options]
                    except json.JSONDecodeError:
                        options = [optionsRaw]
                elif isinstance(optionsRaw, list):
                    options = optionsRaw
                else:
                    options = [optionsRaw]

            # Get answer
            answer = QuestionParser.getField(q, key_cfg("ANSWERS_KEYS", []))

            parsed = {
                "id": q_id,
                "text": question_text,
                "options": options,
                "answer": answer
            }

            current_app.logger.info(f"[Parser] Parsed question: {parsed}")
            return parsed
        
        except Exception as e:
            current_app.logger.error(f"[Parser] Failed to parse question: {e}", exc_info=True)
            return {
                "id": getattr(q, 'id', None),
                "text": None,
                "options": [],
                "answer": None
            }