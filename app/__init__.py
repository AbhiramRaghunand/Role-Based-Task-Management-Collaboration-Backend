from flask import Flask, app
from app.extensions import db
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
from app.routes.tasks import tasks_bp
from app.routes.admin import admin_bp
from dotenv import load_dotenv
from app.utils.response import error_response
import os

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
    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.tasks import tasks_bp
    app.register_blueprint(tasks_bp)
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)  

    @app.errorhandler(404)
    def not_found_error(error):
        return error_response('Resource not found',404)
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response('Internal Server Error',500)
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return error_response('Bad request',400)

    @app.route('/')
    def home():
        return "Welcome to the Flask App"
    
    return app