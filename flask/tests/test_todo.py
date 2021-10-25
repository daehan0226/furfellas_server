# def test_get_todos(client):
#     assert client.get("/api/actions/").status_code == 200


from resources.todos import get_todos


def test_get_todos():
    todos = get_todos()
    assert isinstance(todos, list) 
