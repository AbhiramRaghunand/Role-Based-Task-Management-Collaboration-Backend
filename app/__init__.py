from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

db=SQLAlchemy()
jwt=JWTManager()

def create_app():
    load_dotenv()

    app=Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('DATABASE_URI')
    app.config['JWT_SECRET_KEY']=os.getenv('JWT_SECRET_KEY')

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from app.models.user import User
        # db.create_all()

    @app.route('/')
    def home():
        return "Welcome to the Flask App"
    
    return app