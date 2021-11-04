import os
import string
import random

from flask import request
from flask_restplus import abort
from dotenv import load_dotenv


APP_ROOT = os.path.join(os.path.dirname(__file__), "..")  # refers to application_top
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


def token_required(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        user_info = None
        if auth_header:
            from .db import redis_store, get_user

            user_id = redis_store.get(auth_header)
            if user_id:
                user_info = get_user(user_id)
        return f(*args, **kwargs, user_info=user_info)

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


def random_string(length):
    return "".join(random.choice(string.ascii_letters) for m in range(length))


def random_string_digits(length):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
