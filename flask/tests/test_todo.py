import json
from dateutil.relativedelta import relativedelta

from datetime import datetime


def test_get_todos(client, tables):
    assert client.get("/api/todos/").status_code == 200


def test_get_todos(client, tables):
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
