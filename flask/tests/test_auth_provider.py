import json
from app.core.models import AuthProvider


def test_create_auth_provider_signup(client, api_helpers):

    new_user = AuthProvider("29348013", 9, "wllk2j409")
    result = new_user.create()

    assert result.provider_key == "29348013"
