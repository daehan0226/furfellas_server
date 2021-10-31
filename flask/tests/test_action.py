import json


def test_get_actions(client):
    assert client.get("/api/actions/").status_code == 200


def test_get_action_by_id(client, api_helpers):
    data = {"name": "test-action-by-id"}
    url = "/api/actions/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    action_id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.get(f"/api/actions/{action_id}").status_code == 200


def test_get_action_by_wrong_id(client):
    wrong_id = "23sdf4sdf"
    assert client.get(f"/api/actions/{wrong_id}").status_code == 404


def test_post_action(client, api_helpers):
    name = "test-post-action"
    data = {"name": name}
    post_url = "/api/actions/"
    post_response = client.post(
        post_url, data=json.dumps(data), headers=api_helpers.headers
    )
    action_id = api_helpers.convert_response_to_dict(post_response)["result"]

    get_url = f"/api/actions/{action_id}"
    get_response = client.get(get_url)
    action = api_helpers.convert_response_to_dict(get_response)["result"]

    assert action["name"] == name


def test_get_action_by_name(client, api_helpers):
    name = "test-get-action-by-name"
    data = {"name": name}
    url = "/api/actions/"
    client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    response = client.get(f"/api/actions/?name={name}")
    actions = api_helpers.convert_response_to_dict(response)["result"]

    assert actions[0]["name"] == name


def test_delete_action_by_id(client, api_helpers):
    data = {"name": "test-delete-action"}
    url = "/api/actions/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    action_id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.delete(f"/api/actions/{action_id}").status_code == 204
    assert client.get(f"/api/actions/{action_id}").status_code == 404
