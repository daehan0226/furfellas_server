import os
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, ForeignKey, Table

from flask_sqlalchemy import SQLAlchemy, declarative_base

Base = declarative_base()
db = SQLAlchemy(model_class=Base)

metadata = Base.metadata

association_table = Table(
    "photo_action",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photo.id")),
    Column("action_id", Integer, ForeignKey("action.id")),
)


def get_db_session():
    engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)
