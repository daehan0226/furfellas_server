from core.database import db


class Action(db.Model):
    __tablename__ = "test_action"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f"{self.id} {self.name}"

    def delete(self, id=None, name=None):
        if id is not None:
            Action.query.filter_by(id=id).delete()
        elif name is not None:
            Action.query.filter_by(name=name).delete()
        db.session.commit()
