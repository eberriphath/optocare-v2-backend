from flask import Flask
from app.extensions import db, migrate , cors
from app.config import  Config
from app.models import partner

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from app.models import user, application

    return app