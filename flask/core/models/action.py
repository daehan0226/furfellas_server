from core.database import db, association_table
from sqlalchemy.orm import relationship
from core.models import BaseModel


class Action(BaseModel):
    __tablename__ = "action"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)

    photos = relationship(
        "Photo", secondary=association_table, back_populates="actions"
    )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)
