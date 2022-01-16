import os
from sqlalchemy import event
from core.database import db
from core.models.base import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash


class UserProfile(BaseModel):
    __tablename__ = "user_profile"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    def __init__(self, username, email, password, user_id):
        self.username = username
        self.email = email
        self.set_password(password)
        self.user_id = user_id

    def __repr__(self):
        return self._repr(username=self.username)

    @staticmethod
    def generate_hashed_password(password):
        return generate_password_hash(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


def insert_admin_user_if_not_exist():
    admin = UserProfile.query.filter_by(username=os.getenv("ADMIN_USER_NAME")).all()
    if not admin:
        print("Creating admin user")
        create_admin_user()


def create_admin_user():
    from core.models import User

    admin = User(os.getenv("ADMIN_ROLE_ID"))
    admin_user = admin.create()
    admin_user_profile = UserProfile(
        os.getenv("ADMIN_USER_NAME"),
        os.getenv("ADMIN_USER_EMAIL"),
        os.getenv("ADMIN_USER_PASSWORD"),
        admin_user.id,
    )
    admin_user_profile.create()
    db.session.commit()


@event.listens_for(UserProfile.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    create_admin_user()
