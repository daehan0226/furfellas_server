from datetime import datetime
from dateutil.relativedelta import relativedelta

from core.database import db
from core.models.base import BaseModel


class TodoParent(BaseModel):
    __tablename__ = "todo_parent"
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    repeat_interval = db.Column(db.String(200))
    start_datetime = db.Column(db.DateTime)
    finish_datetime = db.Column(db.DateTime)
    created_datetime = db.Column(db.DateTime, default=datetime.now())
    todo_children = db.relationship("TodoChildren", cascade="all, delete-orphan")

    def __init__(self, task, repeat_interval, start_datetime, finish_datetime):
        self.task = task
        self.repeat_interval = repeat_interval
        self.start_datetime = start_datetime
        self.finish_datetime = finish_datetime

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "task": self.task,
            "repeat_interval": self.repeat_interval,
            "start_datetime": self.start_datetime.isoformat(),
            "finish_datetime": self.finish_datetime.isoformat(),
            "created_datetime": self.created_datetime.isoformat(),
        }

    def set_todo_children(self) -> list:
        result = []
        datetime = self.start_datetime
        if self.repeat_interval == "":
            result.append({"parent_id": self.id, "datetime": datetime})
        elif self.repeat_interval == "1m":
            while datetime < self.finish_datetime:
                result.append({"parent_id": self.id, "datetime": datetime})
                datetime += relativedelta(months=1)
        return result

    def delete(self, id: int):
        if id is not None:
            TodoParent.query.filter_by(id).delete()
            return db.session.commit()


class TodoChildren(BaseModel):
    __tablename__ = "todo_children"
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("todo_parent.id", ondelete="CASCADE"), nullable=False
    )

    def __init__(self, datetime, parent_id):
        self.datetime = datetime
        self.parent_id = str(parent_id)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @staticmethod
    def create_all(objects):
        db.session.add_all(
            [TodoChildren(obj["datetime"], obj["parent_id"]) for obj in objects]
        )
        db.session.commit()

    def delete(self, id):
        if id is not None:
            TodoChildren.query.filter_by(id).delete()
            db.session.commit()
