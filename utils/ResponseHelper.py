from flask import jsonify

def errorResponse(message, status_code=400):
    return {
        "error": message,
        "status": status_code
    }, status_code

def successResponse(data, status_code=200):
    return {
        "data": data,
        "status": status_code
    }, status_code