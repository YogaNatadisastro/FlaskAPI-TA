from services.TokenService import TokenService
from flask import Blueprint, request, jsonify, current_app, session

tokenBp = Blueprint('token', __name__)
tokenService = TokenService()

@tokenBp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get("refresh_token")
    return tokenService.refreshAccessToken(refresh_token)
