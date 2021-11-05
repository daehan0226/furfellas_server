import json


def test_get_user_roles(client):
    assert client.get("/api/user-roles/").status_code == 200


def test_check_user_roles(client, api_helpers):
    user_role_list = api_helpers.convert_response_to_dict(
        client.get(f"/api/user-roles/")
    )["result"]
    user_role_dict = {
        user_role["id"]: user_role["name"] for user_role in user_role_list
    }
    assert user_role_dict[1] == "admin"
    assert user_role_dict[2] == "manager"
    assert user_role_dict[3] == "general"


def test_get_role_by_id(client, api_helpers):
    admin_id = 1
    manager_id = 2
    general_id = 3
    role_admin_response = client.get(f"/api/user-roles/{admin_id}")
    role_manager_esponse = client.get(f"/api/user-roles/{manager_id}")
    role_general_esponse = client.get(f"/api/user-roles/{general_id}")

    assert (
        api_helpers.convert_response_to_dict(role_admin_response)["result"]["name"]
        == "admin"
    )
    assert (
        api_helpers.convert_response_to_dict(role_manager_esponse)["result"]["name"]
        == "manager"
    )
    assert (
        api_helpers.convert_response_to_dict(role_general_esponse)["result"]["name"]
        == "general"
    )


def test_create_test_role(client, api_helpers):
    role_name = "test"
    data = {"name": role_name}
    url = "/api/user-roles/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    manager_id = api_helpers.convert_response_to_dict(response)["result"]
    role_user_esponse = client.get(f"/api/user-roles/{manager_id}")

    assert (
        api_helpers.convert_response_to_dict(role_user_esponse)["result"]["name"]
        == role_name
    )
