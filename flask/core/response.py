import os
import traceback
import json

from flask import Response, current_app, request

from core.constants import response


def return_401_for_no_auth(f):
    def wrapper(*args, **kwargs):
        from core.models import User as UserModel
        from core.models import UserProfile as UserProfileModel
        from resources.sessions import get_session

        user = None
        user_profile = None
        if current_app.config["TESTING"]:
            user_profile = UserProfileModel.query.filter_by(
                username=os.getenv("ADMIN_USER_NAME")
            ).one()
            user = UserModel.query.get(user_profile.user_id)
            return f(*args, **kwargs, auth_user=user, user_profile=user_profile)

        if auth_header := request.headers.get("Authorization"):
            if session := get_session(token=auth_header):
                user = UserModel.query.get(session["user_id"])
                try:
                    user_profile = (
                        UserProfileModel.query.filter_by(user_id=session["user_id"])
                        .one()
                        .serialize
                    )
                except:
                    from resources.oauth_user import verify_google_access_token

                    _, username = verify_google_access_token(auth_header)
                    user_profile = {"username": username}
        if user is not None:
            return f(*args, **kwargs, auth_user=user, user_profile=user_profile)

        else:
            response = CustomeResponse()
            return response.send(response_type="NO_AUTH")

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


def return_500_for_sever_error(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(f"500 error : {e}")
            response = CustomeResponse()
            return response.send(
                response_type="SEVER_ERROR",
            )

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


class CustomeResponse:
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Credentials": "True",
    }

    def send(
        self,
        result=None,
        response_type=None,
        lang="en",
        additional_message=None,
    ):

        status = response.status[response_type]
        message = response.message[lang][response_type]

        if additional_message is not None:
            message += f"({additional_message})"

        response_body = {"result": result, "message": message}

        json_encode = json.JSONEncoder().encode
        return Response(
            json_encode(response_body),
            status=status,
            headers=self.headers,
            mimetype="application/json",
        )


def gen_dupilcate_keys_message(keys, lang="en"):
    if lang == "en":
        return f"The given {(', ').join(keys)} already exist(s)."
    if lang == "kr":
        return f"{(', ').join(keys)} (들)은 이미 존재합니다."
