from flask_restplus import Namespace
from core.models import TodoParent

api = Namespace("todos", description="todos related operations")


def create_todo_parent(**kwargs):
    todo_parent = TodoParent(
        kwargs["task"], kwargs["repeat_interval"],
        kwargs["start_datetime"], kwargs["finish_datetime"]
    )
    todo_parent.create()



todos = [
    {
        'id': 1,
        "task": "Take medicine"
    },
    {
        'id': 2,
        "taks": "Have a bath"
    }
]

def get_todos(id=None):
    if id is not None:
        for todo in todos:
            if todo["id"] == id:
                return todo
    return todos