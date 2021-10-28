import json
from dateutil.relativedelta import relativedelta

from datetime import datetime


def test_get_todos(client):
    assert client.get("/api/todos/").status_code == 200


def test_get_todos_of_parent(client, api_helpers):
    now = datetime.now()
    data = {
        "task": "wake up",
        "repeat_interval": "2m",
        "start_datetime": now.isoformat(" ", "seconds"),
        "finish_datetime": (now + relativedelta(months=11)).isoformat(" ", "seconds"),
    }
    url = "/api/todo-groups/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    parent_id = json.loads(response.data.decode("utf-8"))["result"]

    assert client.get(f"/api/todos/?parent_id={parent_id}").status_code == 200
