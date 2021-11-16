import os
from dotenv import load_dotenv
from datetime import datetime
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
    photo_id = db.Column(db.Integer, db.ForeignKey("photo.id", ondelete="SET NULL"))

    photos = relationship(
        "Photo", secondary=association_table_photo_pet, back_populates="pets"
    )

    def __init__(self, name, weight, birthday, color, intro, photo_id):
        self.name = name
        self.weight = weight
        self.birthday = birthday
        self.color = color
        self.intro = intro
        self.photo_id = photo_id

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        from core.models import Photo

        photo_url = ""
        if self.photo_id:
            image_id = Photo.query.get(self.photo_id).image_id
            photo_url = f"https://drive.google.com/uc?export=view&id={image_id}"

        return {
            "id": self.id,
            "name": self.name,
            "weight": self.weight,
            "intro": self.intro,
            "photo": {"id": self.photo_id, "url": photo_url},
            "birthday": self.birthday.isoformat(),
            "color": self.color,
        }


@event.listens_for(Pet.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    initial_pets = [
        Pet(
            os.getenv("SEVI_NAME"),
            os.getenv("SEVI_WEIGHT"),
            os.getenv("SEVI_BIRTHDAY"),
            os.getenv("SEVI_COLOR"),
            os.getenv("SEVI_INTRO"),
            None,
        ),
        Pet(
            os.getenv("ALBI_NAME"),
            os.getenv("ALBI_WEIGHT"),
            os.getenv("ALBI_BIRTHDAY"),
            os.getenv("ALBI_COLOR"),
            os.getenv("ALBI_INTRO"),
            None,
        ),
    ]
    db.session.add_all(initial_pets)
    db.session.commit()
