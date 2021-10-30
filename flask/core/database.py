import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db = SQLAlchemy()


def get_db_session():
    engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)
