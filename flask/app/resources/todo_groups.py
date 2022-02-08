from flask_restplus import Namespace, reqparse, Resource

from app.core.models import TodoParent
from app.core.response import (
    CustomeResponse,
    exception_handler,
    login_required,
)
from app.core.utils import set_doc_responses


api = Namespace("todo-groups", description="Todo groups related operations")


parser_post = reqparse.RequestParser()
parser_post.add_argument("task", type=str, required=True, help="Task name")
parser_post.add_argument(
    "repeat_interval", type=str, help="Repreat interval(7d, 14d, 2m, 3y)"
)
parser_post.add_argument(
    "start_datetime", type=str, required=True, help="Task start date(year-month-date)"
)
parser_post.add_argument(
    "finish_datetime", type=str, help="Task end date(year-month-date)"
)


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class TodoGroups(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 500))
    @exception_handler
    def get(self):
        """Get all todo-groups"""
        return self.send(response_type="OK", result=TodoParent.get_all_groups())

    @api.doc(responses=set_doc_responses(201, 401, 403, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def post(self, **kwargs):
        """Create a new todo"""
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result = TodoParent.create_todo_group(kwargs["auth_user"].id, args)
            return self.send(response_type="CREATED", result=result.id)
        return self.send(response_type="FORBIDDEN")


@api.doc(params={"id_": "The action identifier"})
@api.route("/<int:id_>")
class TodoGroup(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 404, 500))
    @exception_handler
    def get(self, id_):
        """Get todo by id."""
        if todo := TodoParent.get_by_id(id_):
            return self.send(response_type="OK", result=todo.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 409, 500))
    @api.expect(parser_auth, parser_post)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        """Delete a todo group and recreate todo group."""
        if TodoParent.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                TodoParent.delete_by_id(id_)
                args = parser_post.parse_args()
                result = TodoParent.create_todo_group(kwargs["auth_user"].id, args)
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        """Delete a todo group."""
        if TodoParent.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                TodoParent.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
