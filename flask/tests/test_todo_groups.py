import json
from dateutil.relativedelta import relativedelta

from datetime import datetime


def test_get_todo_groups(client):
    assert client.get("/api/todo-groups/").status_code == 200


def test_get_todo_by_id(client):
    now = datetime.now()

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "wake up",
        "start_datetime": now.isoformat(" ", "seconds"),
    }
    url = "/api/todo-groups/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    id = json.loads(response.data.decode("utf-8"))["result"]
    assert client.get(f"/api/todo-groups/{id}").status_code == 200


def test_create_todo_without_repeat_interval(client):
    now = datetime.now()

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "wake up",
        "start_datetime": now.isoformat(" ", "seconds"),
        "finish_datetime": (now + relativedelta(months=6)).isoformat(" ", "seconds"),
    }
    url = "/api/todo-groups/"

    response = client.post(url, data=json.dumps(data), headers=headers)

    assert response.status_code == 201
    assert isinstance(json.loads(response.data.decode("utf-8"))["result"], int)


def test_create_todo_without_finish_datetime(client):
    now = datetime.now()

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "wake up",
        "start_datetime": now.isoformat(" ", "seconds"),
    }
    url = "/api/todo-groups/"

    response = client.post(url, data=json.dumps(data), headers=headers)

    assert response.status_code == 201
    assert isinstance(json.loads(response.data.decode("utf-8"))["result"], int)


def test_create_todo_without_task(client):
    now = datetime.now()
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "start_datetime": now.isoformat(" ", "seconds"),
        "finish_datetime": (now + relativedelta(months=6)).isoformat(" ", "seconds"),
    }
    url = "/api/todo-groups/"

    response = client.post(url, data=json.dumps(data), headers=headers)

    assert response.status_code == 500


def test_delete_todo_by_id(client):
    now = datetime.now()
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "wake up",
        "start_datetime": now.isoformat(" ", "seconds"),
    }
    url = "/api/todo-groups/"

    response = client.post(url, data=json.dumps(data), headers=headers)
    id = json.loads(response.data.decode("utf-8"))["result"]

    assert client.delete(f"/api/todo-groups/{id}").status_code == 204


def test_get_todo_with_wrong_identifier(client):
    assert client.get(f"/api/todo-groups/34902347903470").status_code == 404
    assert client.get(f"/api/todo-groups/asfwer").status_code == 404


def test_delete_todo_with_wrong_identifier(client):
    assert client.delete(f"/api/todo-groups/34902347903470").status_code == 404
    assert client.delete(f"/api/todo-groups/asfwer").status_code == 404


def test_create_toto_with_todo_children(client):
    now = datetime.now()
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "wake up",
        "repeat_interval": "1m",
        "start_datetime": now.isoformat(" ", "seconds"),
        "finish_datetime": (now + relativedelta(months=6)).isoformat(" ", "seconds"),
    }
    url = "/api/todo-groups/"

    client.post(url, data=json.dumps(data), headers=headers)


def test_set_todo_children(client):
    now = datetime.now()
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "test",
        "repeat_interval": "14d",
        "start_datetime": now.isoformat(" ", "seconds"),
        "finish_datetime": (now + relativedelta(months=6)).isoformat(" ", "seconds"),
    }
    url = "/api/todo-groups/"

    client.post(url, data=json.dumps(data), headers=headers)


def test_get_todo_children(client):
    now = datetime.now()
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "test",
        "repeat_interval": "14d",
        "start_datetime": now.isoformat(" ", "seconds"),
        "finish_datetime": (now + relativedelta(months=6)).isoformat(" ", "seconds"),
    }
    url = "/api/todo-groups/"

    client.post(url, data=json.dumps(data), headers=headers)
