import json


def test_get_users(client):
    assert client.get("/api/users/").status_code == 200


def test_create_user(client, api_helpers):
    data = {"username": "test-create-user", "password": "asdf"}
    url = "/api/users/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)

    assert response.status_code == 201


def test_get_user_by_id(client, api_helpers):
    data = {"username": "test-get-user-by-id", "password": "asdf"}
    url = "/api/users/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    user_id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.get(f"/api/users/{user_id}").status_code == 200


def test_get_user_by_wrong_id(client):
    wrong_id = "0394alkf"

    assert client.get(f"/api/users/{wrong_id}").status_code == 404


def test_get_user_by_name(client, api_helpers):
    username = "test-get-user-by-name"
    data = {"username": username, "password": "asdf"}
    url = "/api/users/"
    client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    response = client.get(f"/api/users/?username={username}")
    users = api_helpers.convert_response_to_dict(response)["result"]

    assert users[0]["username"] == username


def test_get_user_by_wrong_username(client, api_helpers):
    wrong_username = "test-get-user-by-wrong-name"
    response = client.get(f"/api/users/?username={wrong_username}")
    users = api_helpers.convert_response_to_dict(response)["result"]

    assert users == []


def test_get_user_by_email(client, api_helpers):
    email = "test@test.com"
    data = {"username": "test-get-user-by-email", "password": "asdf", "email": email}
    url = "/api/users/"
    client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    response = client.get(f"/api/users/?email={email}")
    users = api_helpers.convert_response_to_dict(response)["result"]

    assert users[0]["email"] == email


def test_get_user_by_wrong_email(client, api_helpers):
    wrong_email = "test-wrong@test.com"
    response = client.get(f"/api/users/?email={wrong_email}")
    users = api_helpers.convert_response_to_dict(response)["result"]

    assert users == []


def test_delete_user_by_id(client, api_helpers):
    data = {"username": "test", "password": "asdf"}
    url = "/api/users/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    user_id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.delete(f"/api/users/{user_id}").status_code == 204
    assert client.get(f"/api/users/{user_id}").status_code == 404


def test_delete_user_by_wrong_id(client):
    wrong_id = "safkk4308"

    assert client.delete(f"/api/users/{wrong_id}").status_code == 404
