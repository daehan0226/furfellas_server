import os
from threading import Thread
from flask import Flask
from flask_cors import CORS

from core.database import db
from core.config import config_by_name
from core.models.user_profile import UserProfile
from core.models.session import Session
from resources.photos import remove_uploaded_file
from resources import blueprint as api
from core.errors import ConfigTypeError

config = None


def start_thread_jobs():
    thread1 = Thread(target=Session.expire_old_session, daemon=True)
    thread2 = Thread(target=remove_uploaded_file, daemon=True)
    thread1.start()
    thread2.start()


def set_db(app):
    with app.app_context():

        db.create_all()
        db.session.commit()
        start_thread_jobs()
        UserProfile.insert_admin_user_if_not_exist()


def create_app(config_name):
    app = Flask(__name__)
    if config_name == "prod":
        app.config.SWAGGER_SUPPORTED_SUBMIT_METHODS = []

    try:
        app_config = config_by_name[config_name]
        app.config.from_object(app_config)
        global config
        config = app_config
    except KeyError:
        raise ConfigTypeError

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    app.register_blueprint(api, url_prefix="/api")

    return app
