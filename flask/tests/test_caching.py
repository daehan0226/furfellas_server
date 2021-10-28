def test_cached_headers(request):
    headers = request.config.cache.get("headers", None)
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"
