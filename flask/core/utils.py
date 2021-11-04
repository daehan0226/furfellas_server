import string
import random

from flask import request, current_app


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


def random_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def random_string_digits(length):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
