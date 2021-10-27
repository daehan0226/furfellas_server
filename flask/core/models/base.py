import sqlalchemy
from datetime import datetime
from typing import Dict, Any


from core.database import db


class BaseModel(db.Model):
    __abstract__ = True

    def __repr__(self):
        return self._repr(id=self.id)

    def _repr(self, **fields: Dict[str, Any]) -> str:
        """
        Helper for __repr__
        """
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f"{key}={field!r}")
            except sqlalchemy.orm.exc.DetachedInstanceError:
                field_strings.append(f"{key}=DetachedInstanceError")
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        result = {}

        for key, value in vars(self).items():
            if isinstance(value, sqlalchemy.orm.state.InstanceState):
                continue
            if isinstance(value, datetime):
                value = value.isoformat()
            result[key] = value
        return result
