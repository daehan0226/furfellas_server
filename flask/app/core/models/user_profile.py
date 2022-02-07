import os

from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.database import db
from app.core.models.base import BaseModel


class UserProfile(BaseModel):
    __tablename__ = "user_profile"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    protected_columns = ["password"]

    def __init__(self, username, email, password, user_id):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.user_id = user_id

    def __repr__(self):
        return self._repr(username=self.username)

    @staticmethod
    def generate_hashed_password(password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def get_user_if_verified(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                return user
        return None

    @property
    def serialize(self):
        return {
            "username": self.username,
            "email": self.email,
            "user_id": self.user_id,
        }

    @classmethod
    def insert_admin_user_if_not_exist(cls):
        admin = cls.query.filter_by(username=os.getenv("ADMIN_USER_NAME")).all()
        if not admin:
            print("Creating admin user")
            cls.create_admin_user()

    @classmethod
    def create_admin_user(cls):
        from app.core.models import User

        admin = User(os.getenv("ADMIN_ROLE_ID"))
        admin_user = admin.create()
        admin_user_profile = cls(
            os.getenv("ADMIN_USER_NAME"),
            os.getenv("ADMIN_USER_EMAIL"),
            os.getenv("ADMIN_USER_PASSWORD"),
            admin_user.id,
        )
        admin_user_profile.create()
        db.session.commit()

    @classmethod
    def update_user(cls, user, arg) -> None:
        if arg["password"] is not None:
            user.password = cls.generate_hashed_password(arg["password"])
        if arg["email"] is not None:
            user.email = arg["email"]
        db.session.commit()

    @classmethod
    def get_user_by_username(cls, username) -> dict:
        user = cls.query.filter_by(username=username).first()
        return user.serialize if user else None

    @classmethod
    def get_user_by_email(cls, email) -> dict:
        user = cls.query.filter_by(email=email).first()
        return user.serialize if user else None

    @classmethod
    def check_user_info_duplicates(cls, args) -> list:
        result = []
        if args.get("username") is not None:
            if cls.get_user_by_username(args.get("username")):
                result.append("username")

        if args.get("email") is not None:
            if cls.get_user_by_email(args.get("email")):
                result.append("email")
        return result

    @classmethod
    def get_users(cls, args) -> list:
        if args.get("username") is not None:
            users = cls.query.filter(cls.username.like(f"%{args.get('username')}%"))

        elif args.get("email") is not None:
            users = cls.query.filter(cls.email.like(f"%{args.get('email')}%"))
        else:
            users = cls.query.all()
        return [user.serialize for user in users]


@event.listens_for(UserProfile.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    UserProfile.create_admin_user()
