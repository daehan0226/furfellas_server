import os
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.orm import relationship
from core.database import db, association_table_photo_pet
from core.models import BaseModel

APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


class Pet(BaseModel):
    __tablename__ = "pet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    weight = db.Column(db.Integer())
    birthday = db.Column(db.DateTime)
    color = db.Column(db.String(6))
    intro = db.Column(db.String(1000))

    photos = relationship(
        "Photo", secondary=association_table_photo_pet, back_populates="pets"
    )

    def __init__(self, name, weight, birthday, color, intro):
        self.name = name
        self.weight = weight
        self.birthday = birthday
        self.color = color
        self.intro = intro

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)


@event.listens_for(Pet.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    initial_pets = [
        Pet(
            os.getenv("SEVI_NAME"),
            os.getenv("SEVI_WEIGHT"),
            os.getenv("SEVI_BIRTHDAY"),
            os.getenv("SEVI_COLOR"),
            os.getenv("SEVI_INTRO"),
        ),
        Pet(
            os.getenv("ALBI_NAME"),
            os.getenv("ALBI_WEIGHT"),
            os.getenv("ALBI_BIRTHDAY"),
            os.getenv("ALBI_COLOR"),
            os.getenv("ALBI_INTRO"),
        ),
    ]
    db.session.add_all(initial_pets)
    db.session.commit()
