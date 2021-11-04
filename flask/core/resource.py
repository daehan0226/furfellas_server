import json
from datetime import date, datetime

from flask import Response
from flask_restplus import Resource


class CustomResource(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    def send(self, *args, **kwargs):
        headers = {}
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
        headers["Access-Control-Allow-Credentials"] = True

        response_body = {}
        response_body["result"] = kwargs.get("result")
        response_body["message"] = kwargs.get("message")

        json_encode = json.JSONEncoder().encode
        return Response(
            json_encode(response_body),
            status=kwargs["status"],
            headers=headers,
            mimetype="application/json",
        )

    def is_admin(self, user_info):
        if user_info is None:
            return False
        if user_info["user_type"] == 0:
            return True
        return False


def response(**kwargs):
    params = ["status", "message", "result"]
    for param in params:
        if kwargs.get(param) is None:
            kwargs[param] = None

    return kwargs
