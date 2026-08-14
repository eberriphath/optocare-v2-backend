from flask import Flask


from app.routes.admin import admin_bp
from app.config import Config
from app.extensions import db, migrate, cors
from app.routes.auth import auth_bp
from app.routes.applications import applications_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from app.models import User, Partner, Application

    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(admin_bp)

    from app.commands import register_commands
    register_commands(app)

    return app