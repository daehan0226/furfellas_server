import traceback
from flask_restplus import Namespace, reqparse, Resource

from core.models import TodoChildren
from core.response import CustomeResponse, return_500_for_sever_error
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
class Todos(Resource, CustomeResponse):
    @api.expect(parser_parent_id)
    @return_500_for_sever_error
    def get(self):
        """ "Get all todos"""
        args = parser_parent_id.parse_args()
        return self.send(
            response_type="SUCCESS", result=get_todos(parent_id=args["parent_id"])
        )
