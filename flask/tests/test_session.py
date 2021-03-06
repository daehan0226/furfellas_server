import json


def test_create_session(client, api_helpers):
    data = {"username": "test-session", "password": "asdf"}
    user_url = "/api/users/"
    client.post(user_url, data=json.dumps(data), headers=api_helpers.headers)

    session_url = "/api/sessions/"
    response = client.post(
        session_url, data=json.dumps(data), headers=api_helpers.headers
    )

    assert response.status_code == 201


def test_validate_session(client, api_helpers):
    data = {"username": "test-session-validate", "password": "asdf"}
    user_url = "/api/users/"
    client.post(user_url, data=json.dumps(data), headers=api_helpers.headers)

    session_url = "/api/sessions/"
    response = client.post(
        session_url, data=json.dumps(data), headers=api_helpers.headers
    )

    res = api_helpers.convert_response_to_dict(response)["result"]
    session_validate_url = "/api/sessions/validate"
    headers = {"Authorization": res["session"], **api_helpers.headers}
    response_validate = client.get(session_validate_url, headers=headers)
    assert response_validate.status_code == 200
