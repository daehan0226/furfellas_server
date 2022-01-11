from threading import Thread
from flask import Flask
from flask_cors import CORS

from core.database import db
from core.config import config_by_name
from resources.photos import remove_uploaded_file
from resources.sessions import expire_old_session
from resources import blueprint as api
from core.errors import ConfigTypeError

config = None


def start_thread_jobs():
    thread1 = Thread(target=expire_old_session, daemon=True)
    thread2 = Thread(target=remove_uploaded_file, daemon=True)
    thread1.start()
    thread2.start()


def set_db(app):
    with app.app_context():

        db.create_all()
        db.session.commit()
        start_thread_jobs()


def create_app(config_name):
    app = Flask(__name__)

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
