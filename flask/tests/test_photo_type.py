import json


def test_get_photo_types(client):
    assert client.get("/api/photo-types/").status_code == 200


def test_get_photo_type_by_id(client, api_helpers):
    data = {"name": "test-photo_type-by-id"}
    url = "/api/photo-types/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    photo_type_id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.get(f"/api/photo-types/{photo_type_id}").status_code == 200


def test_get_photo_type_by_wrong_id(client):
    wrong_id = "23sdf4sdf"
    assert client.get(f"/api/photo-types/{wrong_id}").status_code == 404


def test_post_photo_type(client, api_helpers):
    name = "test-post-photo_type"
    data = {"name": name}
    post_url = "/api/photo-types/"
    post_response = client.post(
        post_url, data=json.dumps(data), headers=api_helpers.headers
    )
    photo_type_id = api_helpers.convert_response_to_dict(post_response)["result"]

    get_url = f"/api/photo-types/{photo_type_id}"
    get_response = client.get(get_url)
    photo_type = api_helpers.convert_response_to_dict(get_response)["result"]

    assert photo_type["name"] == name


def test_get_photo_type_by_name(client, api_helpers):
    name = "test-get-photo_type_by_name"
    data = {"name": name}
    url = "/api/photo-types/"
    client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    response = client.get(f"/api/photo-types/?name={name}")
    photo_types = api_helpers.convert_response_to_dict(response)["result"]
    names = [photo_type["name"] for photo_type in photo_types]

    assert name in names


def test_delete_photo_type_by_id(client, api_helpers):
    data = {"name": "test-delete-photo_type"}
    url = "/api/photo-types/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    photo_type_id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.delete(f"/api/photo-types/{photo_type_id}").status_code == 204
    assert client.get(f"/api/photo-types/{photo_type_id}").status_code == 404
