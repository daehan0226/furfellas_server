from flask import Blueprint, url_for
from flask_restplus import Api
from .photos import api as photos
from .actions import api as actions
from .locations import api as locations
from .todos import api as todos
from .todo_groups import api as todo_groups
from .users import api as users
from .sessions import api as sessions
from .photo_types import api as photo_types
from .user_roles import api as user_roles

blueprint = Blueprint("api", __name__)

class CustomApi(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)

api = CustomApi(blueprint, title="Fur fellas API", version="1.0", description="")

api.add_namespace(photos)
api.add_namespace(photo_types)
api.add_namespace(actions)
api.add_namespace(locations)
api.add_namespace(todos)
api.add_namespace(todo_groups)
api.add_namespace(sessions)
api.add_namespace(users)
api.add_namespace(user_roles)
