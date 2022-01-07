import traceback
from threading import Thread
from flask import Flask
from flask_cors import CORS

from core.database import db
from core.config import config_by_name
from resources.sessions import expire_old_session
from resources import blueprint as api
from core.errors import ConfigTypeError, NoConfigError


def db_schedulers(db_url):
    thread = Thread(target=expire_old_session, args=(db_url,))
    thread.daemon = True
    thread.start()


def set_db(app):
    with app.app_context():

        db.create_all()
        db.session.commit()
        db_schedulers(app.config["SQLALCHEMY_DATABASE_URI"])


def create_app(config_name):
    app = Flask(__name__)

    try:
        app.config.from_object(config_by_name[config_name])
    except KeyError:
        raise ConfigTypeError

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    app.register_blueprint(api, url_prefix="/api")

    return app
