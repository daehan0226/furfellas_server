def test_status(client):
    rs = client.get("/api/locations/")
    assert rs.status_code == 200
