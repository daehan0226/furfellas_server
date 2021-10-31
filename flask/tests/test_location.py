import json


def test_get_locations(client):
    assert client.get("/api/locations/").status_code == 200


def test_get_location_by_id(client, api_helpers):
    data = {"name": "test-location-by-id"}
    url = "/api/locations/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    location_id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.get(f"/api/locations/{location_id}").status_code == 200


def test_get_location_by_wrong_id(client):
    wrong_id = "23sdf4sdf"
    assert client.get(f"/api/locations/{wrong_id}").status_code == 404


def test_post_location(client, api_helpers):
    name = "test-post-location"
    data = {"name": name}
    post_url = "/api/locations/"
    post_response = client.post(
        post_url, data=json.dumps(data), headers=api_helpers.headers
    )
    location_id = api_helpers.convert_response_to_dict(post_response)["result"]

    get_url = f"/api/locations/{location_id}"
    get_response = client.get(get_url)
    location = api_helpers.convert_response_to_dict(get_response)["result"]

    assert location["name"] == name


def test_get_location_by_name(client, api_helpers):
    name = "test-get-location-by-name"
    data = {"name": name}
    url = "/api/locations/"
    client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    response = client.get(f"/api/locations/?name={name}")
    locations = api_helpers.convert_response_to_dict(response)["result"]

    assert locations[0]["name"] == name


def test_delete_location_by_id(client, api_helpers):
    data = {"name": "test-delete-location"}
    url = "/api/locations/"
    response = client.post(url, data=json.dumps(data), headers=api_helpers.headers)
    location_id = api_helpers.convert_response_to_dict(response)["result"]

    assert client.delete(f"/api/locations/{location_id}").status_code == 204
    assert client.get(f"/api/locations/{location_id}").status_code == 404
