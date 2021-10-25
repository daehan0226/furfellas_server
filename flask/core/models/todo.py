from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.database import db


class TodoParent(db.Model):
    __tablename__ = "todo_parent"
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    repeat_interval = db.Column(db.String(200))
    start_datetime = db.Column(db.DateTime)
    finish_datetime = db.Column(db.DateTime)
    created_datetime = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, task, repeat_interval, start_datetime, finish_datetime):
        self.task = task
        self.repeat_interval = repeat_interval
        self.start_datetime = start_datetime
        self.finish_datetime = finish_datetime

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def create_todo_children(self):
        result = []
        datetime = self.start_datetime
        if self.repeat_interval == '1m':
            while datetime < self.finish_datetime:
                result.append({
                    "parent_id": self.id,
                    "datetime": datetime
                })
                datetime += relativedelta(months=6)
        return result

    def __repr__(self):
        return f"{self.id} {self.name}"

    def delete(self, id):
        if id is not None:
            TodoParent.query.filter_by(id).delete()
            db.session.commit()
