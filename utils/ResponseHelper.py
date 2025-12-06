from flask import jsonify
from flask import json

def errorResponse(message, status_code=400):
    response = {
        "success": False,
        "error": message
    }
    return jsonify(response), status_code

def successResponse(message, data=None):
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), 200

def safeJsonLoads(data):
    if isinstance(data, str):
        return json.loads(data)
    return data