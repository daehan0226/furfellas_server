import json
from dateutil.relativedelta import relativedelta

from datetime import datetime


def test_get_todos(client, tables):
    assert client.get("/api/todos/").status_code == 200


def test_get_todo_by_id(client, tables):
    now = datetime.now()

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "wake up",
        "repeat_interval": "1d",
        "start_datetime": now.isoformat(),
        "finish_datetime": (now + relativedelta(months=6)).isoformat(),
    }
    url = "/api/todos/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    id = json.loads(response.data.decode("utf-8"))["result"]
    assert client.get(f"/api/todos/{id}").status_code == 200


def test_create_todos(client, tables):
    now = datetime.now()

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "wake up",
        "repeat_interval": "1d",
        "start_datetime": now.isoformat(),
        "finish_datetime": (now + relativedelta(months=6)).isoformat(),
    }
    url = "/api/todos/"

    response = client.post(url, data=json.dumps(data), headers=headers)

    assert response.status_code == 201
    assert isinstance(json.loads(response.data.decode("utf-8"))["result"], int)


def test_create_todo_without_task(client, tables):
    now = datetime.now()
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "repeat_interval": "1d",
        "start_datetime": now.isoformat(),
        "finish_datetime": (now + relativedelta(months=6)).isoformat(),
    }
    url = "/api/todos/"

    response = client.post(url, data=json.dumps(data), headers=headers)

    assert response.status_code == 500


def test_delete_todo_by_id(client, tables):
    now = datetime.now()
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "wake up",
        "repeat_interval": "1d",
        "start_datetime": now.isoformat(),
        "finish_datetime": (now + relativedelta(months=6)).isoformat(),
    }
    url = "/api/todos/"

    response = client.post(url, data=json.dumps(data), headers=headers)
    id = json.loads(response.data.decode("utf-8"))["result"]

    assert client.delete(f"/api/todos/{id}").status_code == 204


def test_get_todo_with_wrong_identifier(client, tables):
    assert client.get(f"/api/todos/34902347903470").status_code == 404
    assert client.get(f"/api/todos/asfwer").status_code == 404


def test_delete_todo_with_wrong_identifier(client, tables):
    assert client.delete(f"/api/todos/34902347903470").status_code == 404
    assert client.delete(f"/api/todos/asfwer").status_code == 404
