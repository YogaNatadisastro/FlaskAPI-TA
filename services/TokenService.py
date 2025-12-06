from flask import jsonify, current_app
from datetime import datetime, timedelta
from utils.TokenHelper import TokenHelper
from models.token.RefreshToken import RefreshToken
from models import db

class TokenService:

    @staticmethod
    def refreshAccessToken(refreshTokenStr):
        if not refreshTokenStr:
            return jsonify({"message": "Refresh token is missing"}), 400

        payload, error = TokenHelper.DecodeToken(refreshTokenStr, token_type='refresh')
        if error:
            return jsonify({"message": error}), 401
        
        user_id = payload.get("user_id")
        role_id = payload.get("role_id")

        tokenRecord = RefreshToken.query.filter_by(
            user_id=user_id,
            revoked=False
        ).order_by(RefreshToken.created_at.desc()).first()
        
        if tokenRecord is None or not tokenRecord.verify(refreshTokenStr):
            return jsonify({"message": "Refresh token not found or revoked"}), 401

        newAccessToken = TokenHelper.GenerateAccessToken(user_id, role_id)
        newExpiry = tokenRecord.expires_at 

        return jsonify({
            "access_token": newAccessToken,
            "expires_at": newExpiry
        }), 200
    
    @staticmethod
    def revokeRefreshToken(refreshTokenStr):
        tokenRecord = RefreshToken.query.filter_by(
            refresh_token=refreshTokenStr
        ).first()

        if tokenRecord is None:
            return jsonify({"message": "Token not found"}), 404
        
        tokenRecord.revoked = True
        db.session.commit()

        return jsonify({"message": "Token revoked successfully"}), 200
        