from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from core.database import db
from core.models.base import BaseModel


class User(BaseModel):
    __table_name__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100), nullable=False)
    created_datetime = db.Column(db.DateTime, default=datetime.now())

    protected_columns = ["password"]

    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)

    def __repr__(self):
        return f"<User('{self.id}', '{self.username}', '{self.email}')>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
