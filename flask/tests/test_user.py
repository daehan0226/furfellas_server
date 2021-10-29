import json


def test_get_users(client, api_helpers):
    response = client.get("/api/users/")
    users = api_helpers.convert_response_to_dict(response)["result"]
    assert response.status_code == 200
    assert isinstance(users, list)


def test_create_user(client, api_helpers):
    data = {"username": "test", "password": "asdf"}
    url = "/api/users/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.get(f"/api/users/{id}").status_code == 200


def test_delete_user(client, api_helpers):
    data = {"username": "test_delete1112334", "password": "test"}
    url = "/api/users/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.delete(f"/api/users/{id}").status_code == 204
    assert client.get(f"/api/users/{id}").status_code == 404
