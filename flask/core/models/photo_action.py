from core.database import db
from sqlalchemy.orm import relationship, backref
from core.models import BaseModel


class PhotoAction(BaseModel):
    __tablename__ = "photo_action"
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey("Photo.id"))
    action_id = db.Column(db.Integer, db.ForeignKey("Action.id"))
