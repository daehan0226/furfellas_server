import os
import pytest
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


@pytest.fixture()
def db_engine():
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    engine_ = create_engine("sqlite:///test.db", echo=True)

    yield engine_

    engine_.dispose()
