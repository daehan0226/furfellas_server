import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import event
from core.database import db
from core.models.base import BaseModel

APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


class User(BaseModel):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("user_role.id", ondelete="SET NULL"))
    created_datetime = db.Column(db.DateTime, default=datetime.now())

    session = db.relationship("Session", cascade="all, delete-orphan")

    def __init__(self, role_id):
        self.role_id = role_id

    def __repr__(self):
        return self._repr(id=self.id)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def is_admin(self):
        if self.role_id == int(os.getenv("ADMIN_ROLE_ID")):
            return True
        return False

    def is_manager(self):
        if self.role_id == int(os.getenv("MANAGER_ROLE_ID")):
            return True
        return False
