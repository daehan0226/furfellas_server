import traceback
from datetime import datetime
from flask_restplus import Namespace, reqparse


from core.models import TodoParent, TodoChildren
from core.resource import CustomResource


api = Namespace("todo-groups", description="todo groups related operations")


def convert_to_datetime(datetime_, format="%Y-%m-%d %H:%M:%S"):
    return datetime.strptime(datetime_, format)


def create_todo_group(arg):
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
    )
    todo_parent.create()

    todo_children = todo_parent.set_todo_children()
    TodoChildren.create_all(todo_children)

    return todo_parent.id


def get_todo_group(id):
    todo = TodoParent.query.filter_by(id=id).first()
    return todo.serialize if todo else None


def delete_todo_group(id):
    return TodoParent.query.filter_by(id=id).delete()


def get_todo_groups():
    return [todo.serialize for todo in TodoParent.query.all()]


parser_post = reqparse.RequestParser()
parser_post.add_argument("task", type=str, required=True)
parser_post.add_argument("repeat_interval", type=str)
parser_post.add_argument("start_datetime", type=str, required=True)
parser_post.add_argument("finish_datetime", type=str)


@api.route("/")
class TodoGroups(CustomResource):
    def get(self):
        """ "Get all todo-groups"""
        try:
            todo_groups = get_todo_groups()
            return self.send(status=200, result=todo_groups)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.expect(parser_post)
    def post(self):
        """ "Create a new todo"""
        try:
            args = parser_post.parse_args()
            result = create_todo_group(args)
            if result is None:
                return self.send(status=500)
            return self.send(status=201, result=result)

        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<int:id>")
class TodoGroup(CustomResource):
    @api.doc("Get a todo")
    def get(self, id):
        try:
            todo = get_todo_group(id)
            if todo:
                return self.send(status=200, result=todo)
            return self.send(status=404)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("Delete a todo")
    def delete(self, id):
        try:
            if delete_todo_group(id):
                return self.send(status=204)

            return self.send(status=404)
        except:
            traceback.print_exc()
            return self.send(status=500)
