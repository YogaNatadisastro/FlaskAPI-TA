from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_token(self, raw_token: str):
        self.token_hash = generate_password_hash(raw_token)
    
    def verify(self, raw_token: str) -> bool:
        return check_password_hash(self.token_hash, raw_token)