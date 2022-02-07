from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy import asc

from app.core.database import db
from app.core.models.base import BaseModel
from app.core.utils import convert_to_datetime


class TodoParent(BaseModel):
    __tablename__ = "todo_parent"
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    repeat_interval = db.Column(db.String(200))
    start_datetime = db.Column(db.DateTime)
    finish_datetime = db.Column(db.DateTime)
    created_datetime = db.Column(db.DateTime, default=datetime.now())
    todo_children = db.relationship("TodoChildren", cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    def __init__(self, task, repeat_interval, start_datetime, finish_datetime, user_id):
        self.task = task
        self.repeat_interval = repeat_interval
        self.start_datetime = start_datetime
        self.finish_datetime = finish_datetime
        self.user_id = user_id

    def __repr__(self):
        return self._repr(
            id=self.id,
            name=self.task,
            start_datetime=self.start_datetime,
            finish_datetime=self.finish_datetime,
            user_id=self.user_id,
        )

    def _set_intervals(self):
        interval = int(self.repeat_interval[:-1])
        interval_type = self.repeat_interval[-1]

        kwargs = {}
        if interval_type == "m":
            kwargs["months"] = interval
        elif interval_type == "d":
            kwargs["days"] = interval
        elif interval_type == "y":
            kwargs["years"] = interval

        return kwargs

    def set_todo_children(self) -> list:
        datetime = self.start_datetime
        if self.repeat_interval == "":
            return [{"parent_id": self.id, "datetime": datetime}]

        result = []
        while datetime < self.finish_datetime:
            result.append({"parent_id": self.id, "datetime": datetime})
            datetime += relativedelta(**self._set_intervals())
        return result

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
            "user_id": self.user_id,
        }

    @classmethod
    def create_todo_group(cls, user_id, arg):
        start_datetime = convert_to_datetime(arg["start_datetime"])
        finish_datetime = (
            convert_to_datetime(arg["finish_datetime"])
            if arg.get("finish_datetime")
            else start_datetime
        )

        todo_parent = cls(
            arg["task"],
            arg.get("repeat_interval") or "",
            start_datetime,
            finish_datetime,
            user_id,
        )
        todo_parent.create()

        todo_children = todo_parent.set_todo_children()
        TodoChildren.create_all(todo_children)

        return todo_parent

    @classmethod
    def get_all_groups(cls):
        return [todo.serialize for todo in cls.query.all()]


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

    def __repr__(self):
        return self._repr(
            id=self.id,
            datetime=self.datetime,
            parent_id=self.parent_id,
        )

    @classmethod
    def create_all(cls, objects):
        db.session.add_all([cls(obj["datetime"], obj["parent_id"]) for obj in objects])
        db.session.commit()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        from app.core.models import TodoParent

        todo_parent = TodoParent.query.get(self.parent_id)

        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "datetime": self.datetime.isoformat(),
            "task": todo_parent.task,
        }

    @classmethod
    def get_all(cls, **search_filters):
        query = db.session.query(cls)
        if search_filters["parent_id"] is not None:
            query = query.filter(cls.parent_id == search_filters["parent_id"])
        if (
            search_filters["datetime_from"] is not None
            and search_filters["datetime_from"] != ""
        ):
            convert_to_datetime(search_filters["datetime_from"])
            query = query.filter(
                cls.datetime >= convert_to_datetime(search_filters["datetime_from"])
            )
        if (
            search_filters["datetime_to"] is not None
            and search_filters["datetime_to"] != ""
        ):
            query = query.filter(
                cls.datetime
                <= (
                    convert_to_datetime(search_filters["datetime_to"])
                    + relativedelta(days=1)
                )
            )
        query = query.order_by(asc(cls.datetime))
        todos = query.all()
        return [todo.serialize for todo in todos]
