from flask_restplus import Namespace, reqparse, Resource

from core.database import db
from core.models import TodoParent, TodoChildren
from core.response import (
    CustomeResponse,
    return_500_for_sever_error,
    return_401_for_no_auth,
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


def get_todo_group(id):
    todo = TodoParent.query.filter_by(id=id).first()
    return todo.serialize if todo else None


def delete_todo_group(id):
    TodoParent.query.filter_by(id=id).delete()
    db.session.commit()


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
    @return_500_for_sever_error
    def get(self):
        """ "Get all todo-groups"""
        return self.send(response_type="SUCCESS", result=get_todo_groups())

    @api.expect(parser_post, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
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
    @return_500_for_sever_error
    def get(self, id_):
        if todo := get_todo_group(id_):
            return self.send(response_type="SUCCESS", result=todo)
        return self.send(response_type="NOT_FOUND")

    @api.doc("Delete a todo group and recreate todo group")
    @api.expect(parser_auth, parser_post)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def put(self, id_, **kwargs):
        if get_todo_group(id_):
            if kwargs["auth_user"].is_admin():
                delete_todo_group(id_)
                args = parser_post.parse_args()
                result = create_todo_group(kwargs["auth_user"].id, args)
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")

    @api.doc("Delete a todo")
    @api.expect(parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, id_, **kwargs):
        if get_todo_group(id_):
            if kwargs["auth_user"].is_admin():
                delete_todo_group(id_)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")
