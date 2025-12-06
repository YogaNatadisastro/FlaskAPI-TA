from flask import jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from models import db

class UserService:

    @staticmethod
    def updateUsername(user_id, new_username):
        if not new_username:
            return jsonify({'message': 'Username is required'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user.username = new_username

        try:
            db.session.commit()
            return jsonify({
                'message': 'Username updated successfully',
                'data': { 'username': new_username }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
    @staticmethod
    def updatePassword(user_id, old_password, new_password):
        if not old_password or not new_password:
            return jsonify({'message': 'Old and new password are required'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if not check_password_hash(user.password, old_password):
            return jsonify({'message': 'Old password is incorrect'}), 401
        
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        try:
            db.session.commit()
            return jsonify({'message': 'Password updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
    