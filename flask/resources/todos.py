from flask_restplus import Namespace

api = Namespace("todos", description="todos related operations")

def get_todos():
    return []