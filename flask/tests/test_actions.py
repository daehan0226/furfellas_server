def test_get_actions(client):
    assert client.get("/api/actions/").status_code == 200


def test_get_action_by_id(client):
    assert client.get("/api/actions/234512342323").status_code == 404
    assert client.get("/api/actions/asdfer").status_code == 404
    assert client.get("/api/actions/1").status_code == 200


def test_post_action(client):
    assert client.post(f"/api/actions/?name=testing").status_code == 201


def test_get_action_by_name(client):
    assert client.get(f"/api/actions/?name=testing").status_code == 200


def test_delete_action(client):
    assert client.delete(f"/api/actions/?name=testing").status_code == 204
