import json
from datetime import datetime


def test_get_todos(client):
    assert client.get("/api/todos/").status_code == 200


def test_get_todos_of_parent(client, api_helpers, datetime_handler):
    start_datetime = datetime.now()
    finish_datetime = datetime_handler.add_months(start_datetime, 6)
    data = {
        "task": "wake up",
        "repeat_interval": "2m",
        "start_datetime": datetime_handler.serialize(start_datetime),
        "finish_datetime": datetime_handler.serialize(finish_datetime),
    }
    url = "/api/todo-groups/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    parent_id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.get(f"/api/todos/?parent_id={parent_id}").status_code == 200
