import json
import string
import random
import traceback

from flask import request, current_app, Response

from core.constants import response_status
from core.resource import CustomResource


def token_required(f):
    def wrapper(*args, **kwargs):
        user = None
        from core.models import User as UserModel

        if current_app.config["TESTING"]:
            return f(*args, **kwargs, auth_user=UserModel.query.get(1))
        if auth_header := request.headers.get("Authorization"):
            from resources.sessions import get_session

            if session := get_session(token=auth_header):
                user = UserModel.query.get(session["user_id"])
        return f(*args, **kwargs, auth_user=user)

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


def return_500_for_sever_error(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            traceback.print_exc()
            json_encode = json.JSONEncoder().encode
            return Response(
                json_encode(CustomResource.gen_response_body()),
                status=response_status.SEVER_ERROR,
                headers=CustomResource.gen_headers(),
                mimetype="application/json",
            )

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


def random_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def random_string_digits(length):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
