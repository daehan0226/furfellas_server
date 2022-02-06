from flask_restplus import Namespace, reqparse, Resource

from core.models import TodoChildren
from core.response import CustomeResponse, exception_handler

api = Namespace("todos", description="Todos related operations")


parser_search = reqparse.RequestParser()
parser_search.add_argument("parent_id", type=int)
parser_search.add_argument("datetime_from", type=str)
parser_search.add_argument("datetime_to", type=str)


@api.route("/")
class Todos(Resource, CustomeResponse):
    @api.expect(parser_search)
    @exception_handler
    def get(self):
        """Get all todos"""
        args = parser_search.parse_args()
        return self.send(response_type="OK", result=TodoChildren.get_all(**args))
