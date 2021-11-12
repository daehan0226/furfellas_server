from flask_restplus import Namespace, reqparse, Resource

from core.models import TodoChildren
from core.response import CustomeResponse, return_500_for_sever_error
from core.database import db
from core.utils import convert_to_datetime

api = Namespace("todos", description="todos related operations")


def get_todos(**search_filters):
    query = db.session.query(TodoChildren)
    if search_filters["parent_id"] is not None:
        query = query.filter(TodoChildren.parent_id == search_filters["parent_id"])
    if (
        search_filters["datetime_from"] is not None
        and search_filters["datetime_from"] != ""
    ):
        convert_to_datetime(search_filters["datetime_from"])
        query = query.filter(
            TodoChildren.datetime
            >= convert_to_datetime(search_filters["datetime_from"])
        )
    if (
        search_filters["datetime_to"] is not None
        and search_filters["datetime_to"] != ""
    ):
        query = query.filter(
            TodoChildren.datetime <= convert_to_datetime(search_filters["datetime_to"])
        )
    todos = query.all()
    return [todo.serialize for todo in todos]


parser_search = reqparse.RequestParser()
parser_search.add_argument("parent_id", type=int)
parser_search.add_argument("datetime_from", type=str)
parser_search.add_argument("datetime_to", type=str)


@api.route("/")
class Todos(Resource, CustomeResponse):
    @api.expect(parser_search)
    @return_500_for_sever_error
    def get(self):
        """ "Get all todos"""
        args = parser_search.parse_args()
        return self.send(response_type="SUCCESS", result=get_todos(**args))
