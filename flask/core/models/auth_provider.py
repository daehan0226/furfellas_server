from core.database import db
from core.models.base import BaseModel


class AuthProvider(BaseModel):
    __tablename__ = "auth_provider"
    provider_key = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    provider_type = db.Column(db.String(100), nullable=False)

    def __init__(self, provider_key, user_id, provider_type):
        self.provider_key = provider_key
        self.user_id = user_id
        self.provider_type = provider_type

    def __repr__(self):
        return self._repr(provider_key=self.provider_key)
