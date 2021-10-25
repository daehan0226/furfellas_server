from resources.todos import get_todos


def test_get_todos():
    todos = get_todos()
    assert isinstance(todos, list)


def test_get_todo_by_id():
    id = 1
    todo = get_todos(id=id)
    assert todo["id"] == id
