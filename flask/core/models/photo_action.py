from core.database import db
from sqlalchemy.orm import relationship, backref
from core.models import BaseModel
from core.models.photo import Photo
from core.models.action import Action


class PhotoAction(BaseModel):
    __tablename__ = "photo_action"
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey("photo.id"))
    action_id = db.Column(db.Integer, db.ForeignKey("action.id"))

    photo = relationship(
        "Photo", backref=backref("photo_action", cascade="all, delete-orphan")
    )
    action = relationship(
        "Action", backref=backref("photo_action", cascade="all, delete-orphan")
    )
