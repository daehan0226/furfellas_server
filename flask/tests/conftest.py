import os
import pytest
from app import create_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from core.models import Action

from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__), "..")  # refers to application_top
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        with app.test_client() as client:
            yield client


@pytest.fixture()
def db_engine():
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    engine_ = create_engine(os.getenv("SQLALCHEMY_TEST_DATABASE_URI"), echo=True)

    yield engine_

    engine_.dispose()


@pytest.fixture()
def tables(db_engine):
    Action.metadata.create_all(db_engine)
    yield
    Action.metadata.drop_all(db_engine)


@pytest.fixture()
def db_session_factory(db_engine):
    """returns a SQLAlchemy scoped session factory"""
    return scoped_session(sessionmaker(bind=db_engine))


@pytest.fixture()
def db_session(db_session_factory):
    """yields a SQLAlchemy connection which is rollbacked after the test"""
    session_ = db_session_factory()

    yield session_

    session_.rollback()
    session_.close()
