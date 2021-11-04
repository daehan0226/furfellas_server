import os
import json

from flask import Response
from flask_restplus import Resource


class CustomResource(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    def send(self, *args, **kwargs):
        response_body = self.gen_response_body(
            result=kwargs.get("result"), message=kwargs.get("message")
        )

        json_encode = json.JSONEncoder().encode
        return Response(
            json_encode(response_body),
            status=kwargs["status"],
            headers=self.gen_headers(),
            mimetype="application/json",
        )

    @staticmethod
    def gen_headers():
        headers = {}
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
        headers["Access-Control-Allow-Credentials"] = True
        return headers

    @staticmethod
    def gen_response_body(result=None, message=None):
        return {"result": result, "message": message}
