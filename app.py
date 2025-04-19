from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from config.config import Config
from models import db
from routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
