from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
from dotenv import load_dotenv
import os

db=SQLAlchemy()
jwt=JWTManager()
migrate=Migrate()

def create_app():
    load_dotenv()

    app=Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('DATABASE_URI')
    app.config['JWT_SECRET_KEY']=os.getenv('JWT_SECRET_KEY')

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app.models.user import User
        # db.create_all()

    @app.route('/')
    def home():
        return "Welcome to the Flask App"
    
    return app