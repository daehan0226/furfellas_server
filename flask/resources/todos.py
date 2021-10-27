import traceback
from flask_restplus import Namespace, reqparse

from core.models import TodoChildren, TodoParent
from core.resource import CustomResource
from core.database import db

api = Namespace("todos", description="todos related operations")


def get_todos(parent_id=None):
    if parent_id is not None:
        todos = (
            db.session.query(TodoChildren, TodoParent)
            .join(TodoParent, TodoChildren.parent_id == TodoParent.id)
            .filter(TodoParent.id == parent_id)
            .all()
        )
    else:
        todos = (
            db.session.query(TodoChildren, TodoParent)
            .join(TodoParent, TodoChildren.parent_id == TodoParent.id)
            .all()
        )
    serialized_todos = []
    for todo in todos:
        serialized_todo = {}
        child, parent = todo
        serialized_todo.update(child.serialize)
        serialized_todo.update(parent.serialize)
        serialized_todos.append(serialized_todo)
    return serialized_todos


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
