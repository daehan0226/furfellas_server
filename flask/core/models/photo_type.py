from core.database import db
from core.models import BaseModel


class PhotoType(BaseModel):
    __tablename__ = "photo_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)

    def delete(self, id=None, name=None):
        if id is not None:
            PhotoType.query.filter_by(id=id).delete()
        elif name is not None:
            PhotoType.query.filter_by(name=name).delete()
        db.session.commit()
