from core.database import db

from core.models.base import BaseModel


class Location(BaseModel):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)
