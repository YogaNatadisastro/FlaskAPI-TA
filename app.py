from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from config.config import Config
from flask_jwt_extended import JWTManager
from models import db
from routes import api_bp
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    print("ACCESS_TOKEN_SECRET_KEY:", app.config['ACCESS_TOKEN_SECRET_KEY'])
    print("REFRESH_TOKEN_SECRET_KEY:", app.config['REFRESH_TOKEN_SECRET_KEY'])
    print("JWT_SECRET_KEY:", app.config["JWT_SECRET_KEY"])
    print(os.getenv('EXAM_BASE_URL'))

    jwt = JWTManager(app)
    CORS(app)

    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
