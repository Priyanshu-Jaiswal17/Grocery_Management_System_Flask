from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SECRET_KEY"]= 'secret-key'
    app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///grocery_data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.__init__(app)

    from app.routes.auth import auth_bp 
    from app.routes.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    return app

