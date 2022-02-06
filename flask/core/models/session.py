import os
import time
import traceback
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.database import db, get_db_session
from core.models.base import BaseModel
from core.utils import random_string_digits

APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


SESSION_CHECK_TIME_SECONDS = int(os.getenv("SESSION_CHECK_TIME_HOURS")) * 3600
SESSION_VALID_TIME_SECONDS = int(os.getenv("SESSION_VALID_TIME_HOURS")) * 3600


class Session(BaseModel):
    __tablename__ = "session"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(300), unique=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    created_datetime = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, user_id, token=None):
        self.user_id = user_id
        self.token = token if token else self._gen_token()

    def __repr__(self):
        return self._repr(id=self.id, token=self.token, user_id=self.user_id)

    def _gen_token(self):
        self.token = random_string_digits(30)
        return self.token

    @classmethod
    def create(cls, user_id):
        session = cls(user_id)
        db.session.add(session)
        db.session.commit()
        return session

    @classmethod
    def get_session(cls, user_id=None, token=None):
        if user_id is not None:
            session = cls.query.filter_by(user_id=user_id).first()
        elif token is not None:
            session = cls.query.filter_by(token=token).first()
        return session.serialize if session else None

    @classmethod
    def expire_old_session(cls):
        while True:
            try:
                db_scoped_session = get_db_session()
                db_session = db_scoped_session()
                sessions = db_session.query(cls).all()
                for session in sessions:
                    expire_datetime = session.created_datetime + relativedelta(
                        seconds=SESSION_VALID_TIME_SECONDS
                    )
                    if expire_datetime < datetime.now():
                        db_session.query(cls).filter_by(id=session.id).delete()
                        db_session.commit()
                db_scoped_session.remove()
                time.sleep(SESSION_CHECK_TIME_SECONDS)
            except:
                traceback.print_exc()
                break

    @classmethod
    def delete(cls, id_=None, token=None):
        if id_ is not None:
            cls.query.filter_by(user_id=id_).delete()
        elif token is not None:
            cls.query.filter_by(token=token).delete()
        db.session.commit()
