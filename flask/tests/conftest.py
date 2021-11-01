import os
import pytest
import json
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from dotenv import load_dotenv

from app import create_app
from core.database import db

APP_ROOT = os.path.join(os.path.dirname(__file__), "..")  # refers to application_top
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.testing = True
    with app.test_client() as client:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

        with app.app_context():
            db.create_all()
            yield client
            db.session.rollback()
            db.session.close()
            db.drop_all()


@pytest.fixture()
def db_engine():
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    engine_ = create_engine("sqlite:///test.db", echo=True)

    yield engine_

    engine_.dispose()


class ApiCallHelpers:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    @staticmethod
    def convert_response_to_dict(response):
        return json.loads(response.data.decode("utf-8"))


@pytest.fixture
def api_helpers():
    return ApiCallHelpers


class DatetimeHandler:
    @staticmethod
    def add_days(datetime_, days):
        return datetime_ + relativedelta(days=days)

    @staticmethod
    def add_months(datetime_, months):
        return datetime_ + relativedelta(months=months)

    @staticmethod
    def add_years(datetime_, years):
        return datetime_ + relativedelta(years=years)

    @staticmethod
    def serialize(datetime_):
        return datetime_.isoformat(" ", "seconds")


@pytest.fixture
def datetime_handler():
    return DatetimeHandler
