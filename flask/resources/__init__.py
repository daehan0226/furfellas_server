from flask import Blueprint
from flask_restplus import Api
from .logs import api as logs
from .photos import api as photos
from .actions import api as actions
from .locations import api as locations
from .todos import api as todos
from .todo_groups import api as todo_groups

# from .sessions import api as sessions
# from .users import api as users

blueprint = Blueprint("api", __name__)
api = Api(blueprint, title="Fur fellas API", version="1.0", description="")

api.add_namespace(logs)
api.add_namespace(photos)
api.add_namespace(actions)
api.add_namespace(locations)
api.add_namespace(todos)
api.add_namespace(todo_groups)
# api.add_namespace(sessions)
# api.add_namespace(users)
