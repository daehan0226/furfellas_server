import os
from dotenv import load_dotenv


APP_ROOT = os.path.join(os.path.dirname(__file__))
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


class Config:
    """https://flask.palletsprojects.com/en/2.0.x/config"""

    TESTING = False
    DEBUG = False
    ENV = "development"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    broker_url = os.getenv("REDIS_URL")
    result_backend = os.getenv("REDIS_URL")

    SESSION_CHECK_TIME_HOURS = 8
    SESSION_VALID_TIME_HOURS = 1


class ProductionConfig(Config):
    SWAGGER_SUPPORTED_SUBMIT_METHODS = []
    ENV = "production"
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_PROD_DATABASE_URI")


class DevelopmentConfig(Config):
    DEBUG = True
    HOST = os.getenv("DEV_HOST")
    PORT = os.getenv("DEV_PORT")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DEV_DATABASE_URI")


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URI = os.getenv("SQLALCHEMY_TEST_DATABASE_URI")


config_by_name = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)
