from app.core.database import db
from app.core.models import BaseModel


class PhotoAction(BaseModel):
    __tablename__ = "photo_action"
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey("Photo.id", ondelete="CASCADE"))
    action_id = db.Column(db.Integer, db.ForeignKey("Action.id", ondelete="CASCADE"))
