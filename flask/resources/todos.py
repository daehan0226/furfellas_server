import re
from core.models import TodoParent
from datetime import datetime
import traceback
from flask_restplus import Namespace, reqparse
from core.resource import CustomResource
from core import db


api = Namespace("todos", description="todos related operations")


def create_todo_parent(arg):
    now = datetime.now()
    todo_parent = TodoParent("wake up", "1d", now, now)
    todo_parent.create()
    return todo_parent.id


def get_todo(id):
    todo = TodoParent.query.filter_by(id=id).first()
    return todo.serialize if todo else None


def delete_todo(id):
    return TodoParent.query.filter_by(id=id).delete()


def get_todos():
    return [todo_parent.serialize for todo_parent in TodoParent.query.all()]


parser_post = reqparse.RequestParser()
parser_post.add_argument("task", type=str, required=True)
parser_post.add_argument("repeat_interval", type=str, required=True)
parser_post.add_argument("start_datetime", type=str, required=True)
parser_post.add_argument("finish_datetime", type=str, required=True)


@api.route("/")
class Todos(CustomResource):
    def get(self):
        """ "Get all todos"""
        try:
            todos = get_todos()
            return self.send(status=200, result=todos)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.expect(parser_post)
    def post(self):
        """ "Create a new todo"""
        try:
            args = parser_post.parse_args()
            result = create_todo_parent(args)
            if result is None:
                return self.send(status=500)
            return self.send(status=201, result=result)

        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<int:id>")
class Todo(CustomResource):
    @api.doc("Get a todo")
    def get(self, id):
        try:
            todo = get_todo(id)
            if todo:
                return self.send(status=200, result=todo)
            return self.send(status=404)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("Delete a todo")
    def delete(self, id):
        try:
            if delete_todo(id):
                return self.send(status=204)

            return self.send(status=404)
        except:
            traceback.print_exc()
            return self.send(status=500)
