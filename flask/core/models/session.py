from datetime import datetime
from core.database import db
from core.models.base import BaseModel
from core.utils import random_string_digits


class Session(BaseModel):
    __table_name__ = "session"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    created_datetime = db.Column(db.DateTime, default=datetime.now())
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.gen_token()

    def __repr__(self):
        return f"<Session('{self.id}', '{self.token}', '{self.user_id}')>"

    def gen_token(self):
        self.token = random_string_digits(30)
        return self.token

    def delete(self):
        Session.query.filter_by(id=self.id).delete()
        db.session.commit()