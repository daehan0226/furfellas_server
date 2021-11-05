import traceback
import json

from flask import Response, current_app, request

from core.constants.response import (
    status as response_status,
    message as response_message,
)


def return_404_for_no_auth(f):
    def wrapper(*args, **kwargs):
        user = None
        from core.models import User as UserModel

        if current_app.config["TESTING"]:
            return f(*args, **kwargs, auth_user=UserModel.query.get(1))
        if auth_header := request.headers.get("Authorization"):
            from resources.sessions import get_session

            if session := get_session(token=auth_header):
                user = UserModel.query.get(session["user_id"])
            else:
                return CustomeResponse.generate(response_type="NO_AUTH")
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
            return CustomeResponse.generate(
                response_type="SEVER_ERROR",
            )

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


class CustomeResponse:
    @staticmethod
    def generate(status=None, result=None, message=None, response_type=None, lang="en"):
        headers = {}
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
        headers["Access-Control-Allow-Credentials"] = True

        if response_type is not None:
            status = response_status[response_type]
            message = message if message else response_message[lang][response_type]

        response_body = {"result": result, "message": message}

        json_encode = json.JSONEncoder().encode
        return Response(
            json_encode(response_body),
            status=status,
            headers=headers,
            mimetype="application/json",
        )
