from flask_restplus import Namespace, reqparse, Resource

from core.database import db
from core.models import TodoParent, TodoChildren
from core.response import (
    CustomeResponse,
    exception_handler,
    login_required,
)
from core.utils import convert_to_datetime


api = Namespace("todo-groups", description="todo groups related operations")


def create_todo_group(user_id, arg):
    start_datetime = convert_to_datetime(arg["start_datetime"])
    finish_datetime = (
        convert_to_datetime(arg["finish_datetime"])
        if arg.get("finish_datetime")
        else start_datetime
    )

    todo_parent = TodoParent(
        arg["task"],
        arg.get("repeat_interval") or "",
        start_datetime,
        finish_datetime,
        user_id,
    )
    todo_parent.create()

    todo_children = todo_parent.set_todo_children()
    TodoChildren.create_all(todo_children)

    return todo_parent


def get_todo_groups():
    return [todo.serialize for todo in TodoParent.query.all()]


parser_post = reqparse.RequestParser()
parser_post.add_argument("task", type=str, required=True)
parser_post.add_argument("repeat_interval", type=str)
parser_post.add_argument("start_datetime", type=str, required=True)
parser_post.add_argument("finish_datetime", type=str)


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class TodoGroups(Resource, CustomeResponse):
    @exception_handler
    def get(self):
        """ "Get all todo-groups"""
        return self.send(response_type="OK", result=get_todo_groups())

    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def post(self, **kwargs):
        """ "Create a new todo"""
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result = create_todo_group(kwargs["auth_user"].id, args)
            return self.send(response_type="CREATED", result=result.id)
        return self.send(response_type="FORBIDDEN")


@api.route("/<int:id_>")
class TodoGroup(Resource, CustomeResponse):
    @api.doc("Get a todo")
    @exception_handler
    def get(self, id_):
        if todo := TodoParent.get_by_id(id_):
            return self.send(response_type="OK", result=todo.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc("Delete a todo group and recreate todo group")
    @api.expect(parser_auth, parser_post)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        if TodoParent.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                TodoParent.delete_by_id(id_)
                args = parser_post.parse_args()
                result = create_todo_group(kwargs["auth_user"].id, args)
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc("Delete a todo")
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        if TodoParent.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                TodoParent.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
