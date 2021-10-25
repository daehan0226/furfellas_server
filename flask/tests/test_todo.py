def test_get_todos(client):
    assert client.get("/api/todos/").status_code == 200
