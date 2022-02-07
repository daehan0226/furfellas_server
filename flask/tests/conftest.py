import pytest
import json
from dateutil.relativedelta import relativedelta

from app import create_app
from app.core.database import db


@pytest.fixture
def client():
    app = create_app("test")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.rollback()
            db.session.close()


def pytest_sessionfinish(session, exitstatus):
    """whole test run finishes."""
    app = create_app("test")

    with app.app_context():
        db.drop_all()


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
