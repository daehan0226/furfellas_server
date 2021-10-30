from datetime import datetime
from sqlalchemy.orm import relationship
from core.database import db
from core.models import BaseModel


class Photo(BaseModel):
    __tablename__ = "photo"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), unique=True)
    image_id = db.Column(db.String(100), unique=True, nullable=False)
    location_id = db.Column(db.Integer)
    create_datetime = db.Column(db.DateTime, default=datetime.now())
    upload_datetime = db.Column(db.DateTime, default=datetime.now())

    actions = relationship("Action", secondary="photo_action")

    def __init__(
        self, type, description, image_id, location_id, datetime, upload_datetime
    ):
        self.type = type
        self.description = description
        self.image_id = image_id
        self.location_id = location_id
        self.datetime = datetime
        self.upload_datetime = upload_datetime

    def __repr__(self):
        # *args?
        return self._repr(
            id=self.id,
            type=self.type,
            description=self.description,
            image_id=self.image_id,
            location_id=self.location_id,
            datetime=self.datetime,
            upload_datetime=self.upload_datetime,
        )
