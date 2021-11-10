import traceback
from threading import Thread
from flask import Flask
from flask_cors import CORS

from core.database import db
from core.config import config_by_name
from resources.sessions import expire_old_session
from resources import blueprint as api
from core.google_drive_api import init_google_service


def db_schedulers(db_url):
    thread = Thread(target=expire_old_session, args=(db_url,))
    thread.daemon = True
    thread.start()


def init_settings():
    try:
        init_google_service()
    except:
        traceback.print_exc()


def set_db(app):
    with app.app_context():
        # from core import models

        db.create_all()
        db.session.commit()
        db_schedulers(app.config["SQLALCHEMY_DATABASE_URI"])


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    init_settings()
    app.register_blueprint(api, url_prefix="/api")

    return app
