from flask import Flask
from flask_cors import CORS

from resources import blueprint as api


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "ssseetrr"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(api, url_prefix='/api')


    return app
