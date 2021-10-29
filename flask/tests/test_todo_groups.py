import json
from datetime import datetime


def test_get_todo_groups(client):
    assert client.get("/api/todo-groups/").status_code == 200


def test_get_todo_by_id(client, api_helpers, datetime_handler):
    data = {
        "task": "wake up",
        "start_datetime": datetime_handler.serialize(datetime.now()),
    }
    url = "/api/todo-groups/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    id = api_helpers.convert_response_to_dict(response)["result"]
    assert client.get(f"/api/todo-groups/{id}").status_code == 200


def test_create_todo_without_repeat_interval(client, api_helpers, datetime_handler):
    start_datetime = datetime.now()
    finish_datetime = datetime_handler.add_months(start_datetime, 6)
    data = {
        "task": "wake up",
        "start_datetime": datetime_handler.serialize(start_datetime),
        "finish_datetime": datetime_handler.serialize(finish_datetime),
    }
    url = "/api/todo-groups/"

    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    id = api_helpers.convert_response_to_dict(response)["result"]

    assert response.status_code == 201
    assert isinstance(id, int)


def test_create_todo_without_finish_datetime(client, api_helpers, datetime_handler):
    data = {
        "task": "wake up",
        "start_datetime": datetime_handler.serialize(datetime.now()),
    }
    url = "/api/todo-groups/"

    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    id = api_helpers.convert_response_to_dict(response)["result"]

    assert response.status_code == 201
    assert isinstance(id, int)


def test_create_todo_without_task(client, api_helpers, datetime_handler):
    start_datetime = datetime.now()
    finish_datetime = datetime_handler.add_months(start_datetime, 6)
    data = {
        "start_datetime": datetime_handler.serialize(start_datetime),
        "finish_datetime": datetime_handler.serialize(finish_datetime),
    }
    url = "/api/todo-groups/"

    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)

    assert response.status_code == 500


def test_delete_todo_by_id(client, api_helpers, datetime_handler):
    data = {
        "task": "wake up",
        "start_datetime": datetime_handler.serialize(datetime.now()),
    }
    url = "/api/todo-groups/"

    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.delete(f"/api/todo-groups/{id}").status_code == 204


def test_get_todo_with_wrong_identifier(client):
    assert client.get(f"/api/todo-groups/34902347903470").status_code == 404
    assert client.get(f"/api/todo-groups/asfwer").status_code == 404


def test_delete_todo_with_wrong_identifier(client):
    assert client.delete(f"/api/todo-groups/34902347903470").status_code == 404
    assert client.delete(f"/api/todo-groups/asfwer").status_code == 404


def test_create_toto_with_todo_children(client, api_helpers, datetime_handler):
    start_datetime = datetime.now()
    finish_datetime = datetime_handler.add_months(start_datetime, 6)
    data = {
        "task": "wake up",
        "repeat_interval": "1m",
        "start_datetime": datetime_handler.serialize(start_datetime),
        "finish_datetime": datetime_handler.serialize(finish_datetime),
    }
    url = "/api/todo-groups/"

    client.post(url, data=json.dumps(data), headers=api_helpers.headers)


def test_set_todo_children(client, api_helpers, datetime_handler):
    start_datetime = datetime.now()
    finish_datetime = datetime_handler.add_months(start_datetime, 6)
    data = {
        "task": "test",
        "repeat_interval": "14d",
        "start_datetime": datetime_handler.serialize(start_datetime),
        "finish_datetime": datetime_handler.serialize(finish_datetime),
    }
    url = "/api/todo-groups/"

    client.post(url, data=json.dumps(data), headers=api_helpers.headers)
