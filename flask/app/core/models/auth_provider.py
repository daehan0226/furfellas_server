import os
import requests

from app.core.database import db
from app.core.models import BaseModel


class AuthProvider(BaseModel):
    __tablename__ = "auth_provider"
    provider_key = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    provider_type = db.Column(db.String(100), nullable=False)

    def __init__(self, provider_key, provider_type, user_id):
        self.provider_key = provider_key
        self.provider_type = provider_type
        self.user_id = user_id

    def __repr__(self):
        return self._repr(provider_key=self.provider_key)


class GoogleOauthUser:
    provider_type = "google"

    def __init__(self, token):
        self._token = token
        self._provider_key = None
        self._username = None
        self._user_id = None

    @staticmethod
    def return_userinfo_if_token_is_valid(token):
        try:
            url = f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}"
            res = requests.get(url)
            res = res.json()
            return res["sub"], res["name"]

        except Exception as e:
            return None, None

    def verify_token(self):
        provier_key, username = GoogleOauthUser.return_userinfo_if_token_is_valid(
            self._token
        )
        if provier_key and username:
            self._provider_key = provier_key
            self._username = username
            return True
        return False

    def check_if_user_exists(self):
        from app.core.models import AuthProvider

        try:
            oauth_user = AuthProvider.query.filter_by(
                provider_key=self._provider_key
            ).first()
            self._user_id = oauth_user.user_id
            return True
        except:
            return False

    @property
    def username(self):
        return self._username

    def is_admin(self):
        from app.core.models import User

        user = User.query.filter_by(id=self._user_id).one()
        return user.is_admin()

    def create_user(self):
        from app.core.models import AuthProvider, User

        new_user = User(os.getenv("GENERAL_ROLE_ID"))
        new_user.create()
        oauth_user = AuthProvider(
            self._provider_key, GoogleOauthUser.provider_type, new_user.id
        )
        oauth_user.create()
        self._user_id = oauth_user.user_id
