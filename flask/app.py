import os
import traceback
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from core.database import db
from resources.sessions import expire_old_session_job
from resources import blueprint as api
from core.google_drive_api import init_google_service


APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


def db_schedulers():
    expire_old_session_job()


def init_settings():
    try:
        init_google_service()
    except:
        traceback.print_exc()


def set_db(app):
    with app.app_context():
        from core.models import (
            Action,
            Location,
            TodoParent,
            TodoChildren,
            User,
            Session,
            Photo,
            PhotoAction,
        )

        db.create_all()
        db.session.commit()
        db_schedulers()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "ssseetrr"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    init_settings()
    app.register_blueprint(api, url_prefix="/api")

    return app
