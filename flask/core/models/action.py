from core.database import db
from sqlalchemy.orm import relationship
from core.models import BaseModel


class Action(BaseModel):
    __tablename__ = "action"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    photos = relationship("Photo", secondary="photo_action")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)

    def delete(self, id=None, name=None):
        if id is not None:
            Action.query.filter_by(id=id).delete()
        elif name is not None:
            Action.query.filter_by(name=name).delete()
        db.session.commit()
