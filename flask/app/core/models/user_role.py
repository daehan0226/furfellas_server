import os

import sqlalchemy
from sqlalchemy import event

from app.core.database import db
from app.core.models.base import BaseModel


class UserRole(BaseModel):
    __tablename__ = "user_role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(120))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return self._repr(id=self.id, name=self.name, description=self.description)

    @classmethod
    def create_user_role(cls, name, description):
        try:
            user_role = cls(name, description)
            user_role.create()
            return user_role, ""
        except sqlalchemy.exc.IntegrityError as e:
            return False, f"User_role name '{name}' already exists."

    @classmethod
    def get_by_name(cls, name) -> dict:
        user_role = cls.query.filter_by(name=name).first()
        return user_role.serialize if user_role else None

    @classmethod
    def get_user_roles(cls):
        return [user_role.serialize for user_role in cls.query.all()]

    @classmethod
    def update_user_role(cls, id_, name):
        user_role = cls.query.get(id_)
        user_role.name = name
        db.session.commit()


@event.listens_for(UserRole.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    user_roles = [
        UserRole(
            os.getenv("ADMIN_ROLE_NAME"),
            os.getenv("ADMIN_ROLE_DESCRIPTION"),
        ),
        UserRole(
            os.getenv("MANAGER_ROLE_NAME"),
            os.getenv("MANAGER_ROLE_DESCRIPTION"),
        ),
        UserRole(
            os.getenv("GENERAL_ROLE_NAME"),
            os.getenv("GENERAL_ROLE_DESCRIPTION"),
        ),
    ]
    db.session.add_all(user_roles)
    db.session.commit()
