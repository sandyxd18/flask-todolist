import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

from .config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
# metrics = PrometheusMetrics()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
   
    # replace this "https://your-frontend.com" with your actual react domain
    CORS(app, resources={
    r"/*": {
        "origins": ["https://your-frontend.com"],
        "supports_credentials": True
    }
})
    
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from .auth.routes import auth_bp
    from .tasks.routes import tasks_bp
    from .admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    PrometheusMetrics(app, group_by='endpoint')

    return app


def create_admin_user():
    from .models import User
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
    if not admin_password:
        raise ValueError("DEFAULT_ADMIN_PASSWORD is not set in environment variables.")

    if not User.query.filter_by(username='admin').first():
        hashed_pw = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        admin_user = User(
            username='admin',
            password=hashed_pw,  # Ganti sesuai keinginan
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()


__all__ = ['create_app', 'db', 'create_admin_user']
