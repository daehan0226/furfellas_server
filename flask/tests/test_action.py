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


def test_delete_action_by_wrong_id(client):
    wrong_id = 1093195017390182930
    assert client.delete(f"/api/actions/{wrong_id}").status_code == 404


def test_update_action_by_wrong_id(client, api_helpers):
    wrong_id = 1093195017390182930
    data = {"name": "test-update-action-wrong-id"}
    url = f"/api/actions/{wrong_id}"
    response = client.put(url, data=json.dumps(data), headers=api_helpers.headers)

    assert response.status_code == 404


def test_update_action(client, api_helpers):
    name_before_update = "test-update-action-before"
    post_data = {"name": name_before_update}
    post_url = "/api/actions/"
    post_response = client.post(
        post_url, data=json.dumps(post_data), headers=api_helpers.headers
    )
    action_id = api_helpers.convert_response_to_dict(post_response)["result"]

    name_after_update = "test-update-action-after"
    put_data = {"name": name_after_update}
    put_url = f"/api/actions/{action_id}"
    put_response = client.put(
        put_url, data=json.dumps(put_data), headers=api_helpers.headers
    )

    get_url = f"/api/actions/{action_id}"
    get_response = client.get(get_url)
    action_after_update = api_helpers.convert_response_to_dict(get_response)["result"]

    assert put_response.status_code == 204
    assert action_after_update["name"] == name_after_update
