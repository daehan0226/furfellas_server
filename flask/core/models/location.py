import sqlalchemy

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

    @classmethod
    def create(cls, name):
        try:
            location = cls(name)
            db.session.add(location)
            db.session.commit()
            return location, ""
        except sqlalchemy.exc.IntegrityError as e:
            return False, f"Location name '{name}' already exists."

    @classmethod
    def get_all(cls, name=None):
        if name is not None:
            locations = cls.query.filter(cls.name.like(f"%{name}%"))
        else:
            locations = cls.query.all()
        return [location.serialize for location in locations]

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def update(cls, id_, name):
        location = cls.query.get(id_)
        location.name = name
        db.session.commit()
