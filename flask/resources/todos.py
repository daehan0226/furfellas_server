import traceback
from flask_restplus import Namespace, reqparse

from core.models import TodoChildren
from core.resource import CustomResource
from core.database import db

api = Namespace("todos", description="todos related operations")


def get_todos(parent_id=None):
    query = db.session.query(TodoChildren)
    if parent_id is not None:
        query = query.filter(TodoChildren.parent_id == parent_id)
    todos = query.all()
    return [todo.serialize for todo in todos]


parser_parent_id = reqparse.RequestParser()
parser_parent_id.add_argument("parent_id", type=int)


@api.route("/")
class Todos(CustomResource):
    @api.expect(parser_parent_id)
    def get(self):
        """ "Get all todos"""
        try:
            args = parser_parent_id.parse_args()
            todos = get_todos(parent_id=args["parent_id"])
            return self.send(status=200, result=todos)
        except:
            traceback.print_exc()
            return self.send(status=500)
