from datetime import datetime
from sqlalchemy.orm import relationship
from core.database import db, association_table
from core.models import BaseModel


class Photo(BaseModel):
    __tablename__ = "photo"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    image_id = db.Column(db.String(100), unique=True, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("photo_type.id", ondelete="SET NULL"))
    location_id = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="SET NULL")
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    create_datetime = db.Column(db.DateTime, default=datetime.now())
    upload_datetime = db.Column(db.DateTime, default=datetime.now())

    actions = relationship(
        "Action", secondary=association_table, back_populates="photos"
    )

    def __init__(self, **columns):
        self.description = columns["description"]
        self.image_id = columns["image_id"]
        self.type_id = columns["type_id"]
        self.location_id = columns["location_id"]
        self.user_id = columns["user_id"]
        self.create_datetime = columns["create_datetime"]

    def __repr__(self):
        return self._repr(
            id=self.id,
            description=self.description,
            image_id=self.image_id,
            type_id=self.type_id,
            location_id=self.location_id,
            user_id=self.user_id,
            create_datetime=self.create_datetime,
            upload_datetime=self.upload_datetime,
        )

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        from core.models import Location, PhotoType, User

        return {
            "id": self.id,
            "type": PhotoType.query.get(self.type_id).serialize,
            "description": self.description,
            "image_id": self.image_id,
            "user": User.query.get(self.user_id).serialize,
            "create_datetime": self.create_datetime.isoformat(),
            "upload_datetime": self.upload_datetime.isoformat(),
            "location": Location.query.get(self.location_id).serialize,
            "thumbnail": f"https://drive.google.com/thumbnail?id={self.image_id}",
            "original": f"https://drive.google.com/uc?export=view&id={self.image_id}",
            "actions": [action.serialize for action in self.actions],
        }
