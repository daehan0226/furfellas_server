from datetime import datetime
from sqlalchemy.orm import relationship
from core.database import (
    db,
    association_table_photo_action,
    association_table_photo_pet,
)
from core.models import BaseModel


class Photo(BaseModel):
    __tablename__ = "photo"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    image_id = db.Column(db.String(100))
    filename = db.Column(db.String(100), unique=True, nullable=False)
    upload_status = db.Column(db.Integer, default=0)
    location_id = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="SET NULL")
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    create_datetime = db.Column(db.DateTime, default=datetime.now())
    upload_datetime = db.Column(db.DateTime, default=datetime.now())

    actions = relationship(
        "Action", secondary=association_table_photo_action, back_populates="photos"
    )

    pets = relationship(
        "Pet", secondary=association_table_photo_pet, back_populates="photos"
    )

    def __init__(self, **columns):
        self.description = columns["description"]
        self.image_id = ""  # columns["image_id"]
        self.location_id = columns["location_id"]
        self.user_id = columns["user_id"]
        self.create_datetime = columns["create_datetime"]
        self.filename = columns["filename"]

    @staticmethod
    def insert_image_id(photo_id, image_id):
        photo = Photo.get_by_id(photo_id)
        photo.image_id = image_id
        db.session.commit()

    def _upload_status_str(self, status_id):
        return Photo._get_upload_status_list()[status_id]

    @staticmethod
    def _get_upload_status_list():
        return ["waiting", "uploading", "uploaded", "fail"]

    @staticmethod
    def get_upload_status_id(status):
        status_list = Photo._get_upload_status_list()
        return status_list.index(status)

    def __repr__(self):
        return self._repr(
            id=self.id,
            description=self.description,
            image_id=self.image_id,
            location_id=self.location_id,
            user_id=self.user_id,
            create_datetime=self.create_datetime,
            upload_datetime=self.upload_datetime,
        )

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        from core.models import Location, User

        return {
            "id": self.id,
            "description": self.description,
            "image_id": self.image_id,
            "user": User.query.get(self.user_id).serialize,
            "create_datetime": self.create_datetime.isoformat(),
            "upload_datetime": self.upload_datetime.isoformat(),
            "upload_status": self._upload_status_str(self.upload_status),
            "location": Location.query.get(self.location_id).serialize,
            "thumbnail": f"https://drive.google.com/thumbnail?id={self.image_id}"
            if self.image_id
            else "",
            "original": f"https://drive.google.com/uc?export=view&id={self.image_id}"
            if self.image_id
            else "",
            "actions": [action.serialize for action in self.actions],
            "pets": [pet.serialize for pet in self.pets],
        }
