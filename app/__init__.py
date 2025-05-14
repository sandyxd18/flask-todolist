import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

from .models import User
from .config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from .auth.routes import auth_bp
    from .tasks.routes import tasks_bp
    from .admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

def create_admin_user():
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
    if not admin_password:
        raise ValueError("DEFAULT_ADMIN_PASSWORD is not set in environment variables.")

    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password=generate_password_hash(admin_password),  # Ganti sesuai keinginan
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

__all__ = ['create_app', 'db', 'create_admin_user']