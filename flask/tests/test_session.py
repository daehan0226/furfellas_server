import json


def test_create_session(client, api_helpers):
    data = {"username": "test", "password": "asdf"}
    url = "/api/users/"
    client.post(url, data=json.dumps(data), headers=api_helpers.headers)

    url = "/api/sessions/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)

    assert response.status_code == 201


def test_validate_session(client, api_helpers):
    data = {"username": "test", "password": "asdf"}
    url = "/api/users/"
    client.post(url, data=json.dumps(data), headers=api_helpers.headers)

    url = "/api/sessions/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    session = api_helpers.convert_response_to_dict(response)["result"]
    url = "/api/sessions/validate"
    headers = {"Authorization": session, **api_helpers.headers}
    response_validate = client.get(url, headers=headers)
    assert response_validate.status_code == 200
