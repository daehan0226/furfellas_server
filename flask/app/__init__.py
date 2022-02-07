import os
from threading import Thread
from flask import Flask
from flask_cors import CORS
from celery import Celery

from app.core.database import db
from config import config_by_name, Config
from app.core.errors import ConfigTypeError

config = None

celery = Celery(__name__, broker=Config.broker_url)


def start_thread_jobs():
    from app.core.models import Session, Photo

    thread1 = Thread(target=Session.expire_old_session, daemon=True)
    thread2 = Thread(target=Photo.remove_uploaded_file, daemon=True)
    thread1.start()
    thread2.start()


def set_db(app):
    from app.core.models import UserProfile

    with app.app_context():

        db.create_all()
        db.session.commit()
        start_thread_jobs()
        UserProfile.insert_admin_user_if_not_exist()


def create_app(config_name=None):
    app = Flask(__name__)
    if config_name == "prod":
        app.config.SWAGGER_SUPPORTED_SUBMIT_METHODS = []

    try:
        if config_name is None:
            config_name = "dev"
        app_config = config_by_name[config_name]
        app.config.from_object(app_config)
        global config
        config = app_config

        celery.conf.update(app.config)
    except KeyError:
        raise ConfigTypeError

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    from app.resources import blueprint as api

    app.register_blueprint(api, url_prefix="/api")

    return app
