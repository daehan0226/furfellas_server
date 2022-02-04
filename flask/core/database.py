import os

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, ForeignKey, Table
from flask_sqlalchemy import SQLAlchemy, declarative_base


Base = declarative_base()
db = SQLAlchemy(model_class=Base)

metadata = Base.metadata

association_table_photo_action = Table(
    "photo_action",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photo.id", ondelete="CASCADE")),
    Column("action_id", Integer, ForeignKey("action.id", ondelete="CASCADE")),
)


association_table_photo_pet = Table(
    "photo_pet",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photo.id", ondelete="CASCADE")),
    Column("pet_id", Integer, ForeignKey("pet.id", ondelete="CASCADE")),
)


def get_db_session():
    from app import config

    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)
