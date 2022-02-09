import os
from dotenv import load_dotenv


APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


class Config:
    """https://flask.palletsprojects.com/en/2.0.x/config"""

    TESTING = False
    DEBUG = False
    ENV = "development"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    broker_url = os.getenv("REDIS_URL_DEV")
    result_backend = os.getenv("REDIS_URL_DEV")

    SESSION_CHECK_TIME_HOURS = 8
    SESSION_VALID_TIME_HOURS = 1
    REMOVE_IMAGE_INTERVAL_HOURS = 24

class ProductionConfig(Config):
    SWAGGER_SUPPORTED_SUBMIT_METHODS = []
    ENV = "production"
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    db_url = f'mysql+pymysql://{os.getenv("MYSQL_USER")}:{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL")}:{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}'
    print(db_url)
    SQLALCHEMY_DATABASE_URI = db_url
    #SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_PROD_DATABASE_URI")
    redis=f'redis://:{os.getenv("REDIS_PASSWORD")}@{os.getenv("REDIS")}:{os.getenv("REDIS_PORT")}/0'
    REDIS_URL = redis
    broker_url = redis
    result_backend = redis


class DevelopmentConfig(Config):
    DEBUG = True
    HOST = os.getenv("DEV_HOST")
    PORT = os.getenv("DEV_PORT")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DEV_DATABASE_URI")
    REDIS_URL = os.getenv("REDIS_URL_DEV")

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URI = os.getenv("SQLALCHEMY_TEST_DATABASE_URI")
    REDIS_URL = os.getenv("REDIS_URL_DEV")

config_by_name = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)
