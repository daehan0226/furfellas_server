from core.models import TodoParent

import traceback
from flask_restplus import Namespace, reqparse
from core.resource import CustomResource
from core import db


api = Namespace("todos", description="todos related operations")


def create_todo_parent(task, rpeat_interval, start_datetime, finish_datetime):
    todo_parent = TodoParent(task, rpeat_interval, start_datetime, finish_datetime)
    todo_parent.create()


def get_todos():
    return TodoParent.query.all()


@api.route("/")
class Actions(CustomResource):
    @api.doc("Get all todos")
    def get(self):
        try:
            todos = get_todos()
            return self.send(status=200, result=todos)
        except:
            traceback.print_exc()
            return self.send(status=500)
