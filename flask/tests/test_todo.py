import json
from dateutil.relativedelta import relativedelta

from datetime import datetime


def test_get_todos(client, tables):
    assert client.get("/api/todos/").status_code == 200


def test_get_todos_of_parent(client, tables):
    now = datetime.now()

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "task": "wake up",
        "repeat_interval": "2m",
        "start_datetime": now.isoformat(),
        "finish_datetime": (now + relativedelta(months=11)).isoformat(),
    }
    url = "/api/todo-groups/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    parent_id = json.loads(response.data.decode("utf-8"))["result"]

    assert client.get(f"/api/todos/?parent_id={parent_id}").status_code == 200
