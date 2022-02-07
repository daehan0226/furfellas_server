from flask_restplus import Resource

from app.core.response import CustomeResponse


class CustomResource(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    def send(self, *args, **kwargs):
        return CustomeResponse.generate(
            kwargs.get("status"),
            result=kwargs.get("result"),
            message=kwargs.get("message"),
            response_type=kwargs.get("response_type"),
        )
