from datetime import datetime
from sqlalchemy.orm import relationship
from core.database import db
from core.models import BaseModel, Location


class Photo(BaseModel):
    __tablename__ = "photo"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    image_id = db.Column(db.String(100), unique=True, nullable=False)
    location_id = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="SET NULL")
    )
    create_datetime = db.Column(db.DateTime, default=datetime.now())
    upload_datetime = db.Column(db.DateTime, default=datetime.now())

    actions = relationship("Action", secondary="photo_action")

    def __init__(self, **columns):
        self.type = columns["type"]
        self.description = columns["description"]
        self.image_id = columns["image_id"]
        self.location_id = columns["location_id"]
        self.create_datetime = columns["create_datetime"]

    def __repr__(self):
        return self._repr(
            id=self.id,
            type=self.type,
            description=self.description,
            image_id=self.image_id,
            location_id=self.location_id,
            create_datetime=self.create_datetime,
            upload_datetime=self.upload_datetime,
        )

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "image_id": self.image_id,
            "create_datetime": self.create_datetime.isoformat(),
            "upload_datetime": self.upload_datetime.isoformat(),
            "location": Location.query.get(self.location_id).serialize,
            "actions": [action.serialize for action in self.actions],
        }
