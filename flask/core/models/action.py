import sqlalchemy
from sqlalchemy.orm import relationship
from core.database import db, association_table_photo_action
from core.models import BaseModel


class Action(BaseModel):
    __tablename__ = "action"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)

    photos = relationship(
        "Photo", secondary=association_table_photo_action, back_populates="actions"
    )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)

    @classmethod
    def create(cls, name):
        try:
            action = cls(name)
            db.session.add(action)
            db.session.commit()
            return action, ""
        except sqlalchemy.exc.IntegrityError as e:
            return False, f"Action name '{name}' already exists."

    @classmethod
    def get_all(cls, name=None):
        if name is not None:
            actions = cls.query.filter(cls.name.like(f"%{name}%"))
        else:
            actions = cls.query.all()
        return [action.serialize for action in actions]

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def update(cls, id_, name):
        action = cls.query.get(id_)
        action.name = name
        db.session.commit()
